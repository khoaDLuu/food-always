from bs4 import BeautifulSoup
import time
import os
import json
import re
import random

from ..mongodb.mongo_client import mongo_client
from .get_html_text import get_html_text, HTMLGetError
from .base_dir import base_dir


class DataWriteError(Exception):
    pass


class HTMLParserError(Exception):
    pass


class ERROR404(Exception):
    pass


class URLERROR(Exception):
    pass


def html_text_parse(text, random_id, food_id):

    soup = BeautifulSoup(text, "html.parser")

    # Get food name + picture
    food_info = soup.find('a', class_="J_photo")
    # The name of the food
    title = food_info['title']
    # Get food picture
    image_url = food_info.img['src']

    while True:
        try:
            image = get_html_text(url=image_url, tag=False)
        except Exception as e:
            print(e)
            if "404 Client Error" in str(e):
                print("404 Changed the operating error, execution...")
                return
            else:
                print("Details pictures for failure, try again")
                time.sleep(0.1)
                continue
        else:
            path = os.path.join(base_dir, "food_article", random_id)
            with open(os.path.join(path, 'full.jpg'), 'wb') as f:
                f.write(image)
            break
    image_path = os.path.join("food_article", random_id, 'full.jpg')

    # Find the description text
    try:
        desc = soup.find('div', id="block_txt1").text
    except:
        desc = ""

    # Extract data of food ingredient > ingredients
    ingredients = soup.find_all("fieldset", class_="particulars")
    ingredients_list = []
    for ingredient in ingredients:
        name = ingredient.legend.text
        formulas = ingredient.find_all('li')
        ingredient_data = {}
        for formula in formulas:
            formula_name = formula.find('span', class_="category_s1").b.text
            formula_dosage = formula.find('span', class_="category_s2").text
            ingredient_data[formula_name] = formula_dosage
        ingredients_list.append({
            "name": name,
            "formulas": ingredient_data
        })

    # Find step information
    steps = soup.find('div', class_="recipeStep").find_all('li')
    steps_list = []
    for step in steps:
        step_number = step.find("div", class_="recipeStep_word").div.text
        step_info = step.find("div", class_="recipeStep_word").text
        step_info = step_info.replace(step_number, "")

        try:
            step_image_url = step.find("div", class_="recipeStep_img").img['src']
            if "blank.gif" in step_image_url:
                raise URLERROR
            while True:
                try:
                    image = get_html_text(url=step_image_url, tag=False)
                    step_path = os.path.join(base_dir, "food_article", random_id, 'step')
                    if not os.path.isdir(step_path):
                        os.makedirs(step_path)
                    with open(os.path.join(step_path, f'step_image_{step_number}.jpg'), 'wb') as f:
                        f.write(image)
                    break
                except HTMLGetError as e:
                    if "404 Client Error" in str(e):
                        raise ERROR404("404 error appears in the step picture")
                    print(e)
                    print("Failed to get the step picture, try to get it again")
                    time.sleep(0.1)
                    continue
            step_image_path = os.path.join("food_article", random_id, 'step', f'step_image_{step_number}.jpg')
        except Exception:
            step_image_path = ""

        step_image_url_info = str(step.find("div", class_="recipeStep_img").img)
        steps_list.append({
            'step_number': step_number,
            "step_info": step_info,
            "step_image_path": step_image_path,
            "step_image_url_info": step_image_url_info
        })

    # Get tips
    tip = soup.find('div', class_='recipeTip')
    if tip:
        tip_info = tip.text
    else:
        tip_info = ""

    # For classification
    tags = soup.find_all('div', class_='recipeTip mt16')[-1].find_all('a')
    tags_list = []
    for tag in tags:
        tags_list.append(tag.text)

    # For evaluation, ajax loading of data
    ajax_url = "FOOD_WEBSITE_AJAX_URL".format(food_id)
    try:
        evaluation = get_html_text(ajax_url)
        evaluation_data = json.loads(evaluation)
        like = evaluation_data["likenum"]
        fav = evaluation_data["ratnum"]
    except:
        print("Ajax data fetching failed, using random data")
        like = random.randint(100, 600)
        fav = random.randint(600, 6000)

    # Data aggregation
    data = {
        "title": title,
        "image_path": image_path,
        "random_id": random_id,
        "desc": desc,
        "ingredients_list": ingredients_list,
        "steps_list": steps_list,
        "tip_info": tip_info,
        "tags_list": tags_list,
        "evaluation": {"like": like, 'fav': fav}
    }

    return data


def run():

    # Get food link information in MongoDB database
    url_conn = mongo_client()
    food_data = url_conn.food.food_rank.find({}).batch_size(10)


    # When the page is parsed incorrectly, collect the wrong URL information
    error_list = []

    print("A total of 482 (?) pages to be obtained...")
    all_urls = 482
    count = 1
    for food in food_data:
        url = food["food_detail_url"]
        random_id = food["random_id"]
        pattern = re.compile(r'.*-(\d*)\.html')
        food_id = pattern.search(url).group(1)

        print(f"Start to get the information of the {count} page")
        print(f'Page url> {url}')
        while True:
            try:
                text = get_html_text(url)
                time.sleep(0.1)
                data = html_text_parse(text, random_id, food_id)
            except HTMLGetError as e:
                print(e)
                print("Trying to get it again")
                continue
            except Exception as e:
                print(f"Page parsing error {e}")
                error_list.append({
                    "url": url,
                    "random_id": random_id,
                    "error_info": str(e)
                })
                count += 1
                break
            else:
                if data:
                    db_client = mongo_client()
                    db_client.food.food_data.insert_one(data)
                    db_client.close()
                    print(
                        f"Page {count}'s information extraction is complete... "
                        f"{all_urls - count - len(error_list)} pages remaining, "
                        f"Failed extracting for {len(error_list)} pages"
                    )
                    count += 1
                    break
                else:
                    error_info = "404 error page"
                    print(error_info)
                    error_list.append({
                        "url": url,
                        "random_id": random_id,
                        "error_info": error_info
                    })
                    count += 1
                    break

    url_conn.close()

    print("All pages completed...")
    if error_list:
        with open("error.txt", 'w') as f:
            json.dump(error_list, f)


if __name__ == '__main__':
    run()
