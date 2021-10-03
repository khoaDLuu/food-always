"""
Crawl pictures from this picture website: https://www.pexels.com/
Since the picture is dynamically loaded,
    the response returned is a js function,
    so the url of the picture is matched by re
Then use the matching url to get the picture
"""

import re
import os
import time
import threading
from queue import Queue

from bs4 import BeautifulSoup as bs
import requests
from hanziconv import HanziConv

from .base_dir import base_dir
from .food_rank_crawler import create_random_string
from .get_html_text import get_html_text, create_headers
from ..mongodb.mongo_client import mongo_client


class DataIncomplete(Exception):
    pass


def get_image_url(text):
    """Analyze the dynamically loaded image url of the webpage"""
    low_pattern = re.compile('<a (.*?)>')
    high_pattern = re.compile(r'(/en/photo/\d*/)')
    all_url = low_pattern.findall(text)[2:-2]
    url_list = []
    for url in all_url:
        try:
            short_url = high_pattern.search(url)
            if short_url:
                long_url = "https://www.pexels.com" + short_url.group(1)
                url_list.append(long_url)
        except Exception as e:
            print("Regular expression match error, execute the next match...")
            print(f"Cause of error: {e}")
            continue
    return url_list


def image_parser(text, refer_page):
    """Analyze the picture webpage and save it locally and to MongoDB"""
    soup = bs(text, 'html.parser')

    # Get pictures
    image_url = soup.find(
        'div', class_="photo-page__photo"
    ).find('a', class_="js-photo-page-image-download-link").find(
        'img', class_="js-photo-page-image-img"
    )['data-zoom-src']
    random_id = create_random_string()
    count = 1
    while True:
        try:
            head = create_headers()
            with requests.get(url=image_url, headers=head[0], proxies=head[1], timeout=30, stream=True) as image:
                path = os.path.join(base_dir, "food_image", random_id)
                if not os.path.isdir(path):
                    os.makedirs(path)
                with open(os.path.join(path, f'{random_id}-full.jpg'), 'wb') as f:
                    image_data = b''
                    for chunk in image.iter_content(chunk_size=1024):
                        image_data += chunk
                    # If the content length of the response body is less than the length given in the header,
                    # an error will occur, and the picture will be retrieved again
                    if len(image_data) < int(image.headers['content-length']):
                        raise DataIncomplete("The picture response body data is incomplete, get it again...")
                    f.write(image_data)
                    print("Response body data read completed...")
            break
        except Exception as e:
            print(e)
            if "404 Client Error" in str(e):
                print("full-image get 404 error, perform skip operation...")
                return
            else:
                print("full-image fetching failed, try to get it again")
                time.sleep(0.1)
                count += 1
                if count > 20:
                    print("Retried the operation 20 times, perform the skipped operation...")
                    return
                else:
                    continue

    tags_list = []
    tags = soup.find("div", class_="photo-page__related-tags").find_all('li')
    if tags:
        for tag in tags:
            tags_list.append(HanziConv.toSimplified(tag.a.text))

    # Get image tag
    data = {
        "random_id": random_id,
        "image_path": os.path.join("food_image", random_id, f'{random_id}-full.jpg'),
        "tags_list": tags_list,
    }

    return data


def run(url, i):
    """Given url, crawl the picture list page, get the address of a single picture and crawl it"""
    data = []

    print(f"Start to crawl the picture on page {i} ...")
    while True:
        try:
            js_text = get_html_text(url)
        except Exception as e:
            print(e)
            if "404 Client Error" in str(e):
                print("404 error occurs when getting dynamic js file, skip operation...")
                return
            else:
                print("Failed to get the dynamic js file, trying to get it again")
                time.sleep(0.1)
                continue
        else:
            image_url_list = get_image_url(js_text)
            if image_url_list:
                count = 1
                for image_url in image_url_list:
                    while True:
                        try:
                            image_text = get_html_text(image_url)
                        except Exception as e:
                            print(e)
                            if "404 Client Error" in str(e):
                                print(
                                    f"Failed to crawl the picture {count} on page {i}. "
                                    "Reason: a 404 error occurred when the picture was obtained, "
                                    "and the skip operation was performed..."
                                )
                                count += 1
                                break
                            else:
                                print("Failed to get the picture, try to get it again")
                                time.sleep(0.1)
                                continue
                        else:
                            image_data = image_parser(image_text, image_url)
                            if image_data:
                                data.append(image_data)
                                print(f"Done crawling the picture {count} on page {i}")
                                count += 1
                                break
                            else:
                                print(
                                    "After many attempts, "
                                    f"failed to get the picture {count} on page {i} ..."
                                )
                                count += 1
                                break

            break

    conn = mongo_client()
    for item in data:
        conn.food.food_image.insert_one(item)
    conn.close()
    print(f"The image crawling on page {i} is complete...")


class GetImage(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            item = self.queue.get()
            print(item)
            run(item[0], item[1])
            self.queue.task_done()


def main():
    url_queue = Queue()
    for i in range(30, 60):
        url = f"PEXEL_WEBSITE_URL"
        url_queue.put((url, i))
    t1 = GetImage(url_queue)
    t2 = GetImage(url_queue)
    t3 = GetImage(url_queue)
    t4 = GetImage(url_queue)
    t1.start()
    time.sleep(0.2)
    t2.start()
    time.sleep(0.2)
    t3.start()
    time.sleep(0.2)
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()


if __name__ == '__main__':
    main()
