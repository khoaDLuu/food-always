import random
import time
import os

from bs4 import BeautifulSoup as bs
from django.conf import settings

from ..mongodb.mongo_client import mongo_client
from .get_html_text import get_html_text, HTMLGetError
from .base_dir import base_dir


def create_random_string():
    stings = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"
    random_string = "".join(random.sample(stings, 4))
    return f'{int(time.time())}-{random_string}'


def food_rank_parser(text):

    data = []
    soup = bs(text, "html.parser")
    # Get all records
    ranks = soup.find('div', attrs={'class': "ui_newlist_1 get_num"}).find_all('li')
    for rank in ranks:
        # Get the data of a single record
        description = rank.find('div', class_="pic")
        detail = rank.find('div', class_="detail")

        # Random id for food
        random_id = create_random_string()

        if "blank.gif" in description.a.img["src"]:
            image_url = description.a.img["data-src"]
        else:
            image_url = description.a.img["src"]
        try:
            image = get_html_text(url=image_url, tag=False)
            time.sleep(0.1)
        except HTMLGetError as e:
            print(e)
            print("Failed to get the picture, skip this record")
            continue
        else:
            # Write the picture to the file system
            path = os.path.join(base_dir, "food_article", random_id)
            if not os.path.isdir(path):
                os.makedirs(path)
            with open(os.path.join(path, 'sample.jpg'), 'wb') as f:
                f.write(image)

        # Get food name
        name = detail.h2.a.text.strip()
        # Get food details link
        food_detail_url = detail.h2.a["href"]
        # Get the author of the food
        author = detail.find('p', class_="subline").a.text
        # Get the food ingredient list
        ingredient_list = detail.find('p', class_="subcontent").text

        data.append({
            "name": name,
            "random_id": random_id,
            "image_path": os.path.join("food_article", random_id, 'sample.jpg'),
            "food_detail_url": food_detail_url,
            "author": author,
            "ingredient_list": ingredient_list,
        })

    return data


def run():
    rank_data = []
    for page in range(20, 51):
        print(f"Getting page {page}'s data...")
        food_rank_url = settings.FOOD_WEBSITE_RANKING_URL.format(page=page)

        if page == 1:
            refer_url = settings.FOOD_WEBSITE_REFERRER_URL
        else:
            refer_url = settings.FOOD_WEBSITE_RANKING_URL.format(page=page - 1)

        text = get_html_text(url=food_rank_url, refer_page=refer_url)
        data = food_rank_parser(text)
        rank_data.extend(data)
        print(f"Data extraction on page {page} is complete!")

    print("Done extracting data, starting to write data...")

    client = mongo_client()
    for data in rank_data:
        client.food.food_rank.insert_one(data)
    # If you need to modify the serial number, you can directly call insert_many(rank_data)
    # The parameter passed in is a list, and the elements in the list are dictionary tables
    # client.food.food_rank.insert_many(rank_data)

    print("Data writing completed")


if __name__ == '__main__':
    run()
