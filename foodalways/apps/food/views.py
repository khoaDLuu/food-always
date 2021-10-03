"""
View-related categories of food,
including rankings, article details, all pictures, and single pictures
Function to convert data from MongoDB to PostgresSQL
"""

import random
import os
from PIL import Image

from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, PageNotAnInteger
from django_food.settings import BASE_DIR
from django.db.models import Q

from assist_function.mongodb.mongo_client import mongo_client
from .models import FoodArticle, Tags, FoodSteps, FoodImage, ImageTags, FoodIngredients


class FoodRankingView(View):

    def get(self, request):
        food_list = FoodArticle.objects.order_by("-like")
        popular_food = FoodArticle.objects.order_by("-fav")[:3]

        message = bool(food_list)

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Page all objects retrieved from the database,
        # the middle parameter is the number of objects displayed on each page,
        # the default is set to 6
        paginator = Paginator(food_list, 12, request=request)
        food_list_page = paginator.page(page)

        return render(request, 'food/food_ranking.html', {
            "food_list": food_list_page,
            "popular_food": popular_food,
            "message": message,
            "focus": "article",
        })


class FoodArticleView(View):

    def get(self, request, article_id):

        popular_food = FoodArticle.objects.all().order_by("-fav")[:3]
        food = FoodArticle.objects.get(article_id=article_id)

        food.click_number += 1
        food.save()

        print(food.image.url)
        path = '/'.join(food.image.url.split("/")[2:-1])
        # print(str(food.image))
        # print(path)
        # path = os.path.split(food.image.name)[0]
        food_image = os.path.join(path, 'full.jpg')
        food_image = food_image
        print(food_image)

        food_steps = FoodSteps.objects.filter(article_id=article_id).order_by('step_number')

        # Data is dumped from MongoDB to PostgresSQL, so there is no need
        # to extract ingredient information from the MongoDB database
        # conn = mongo_client()
        # food_info = conn.food.food_data.find_one({"random_id": article_id})
        # conn.close()

        food_info = FoodIngredients.objects.filter(article_id=article_id)
        food_info_1 = food_info.filter(classification='1')
        food_info_2 = food_info.filter(classification='2')
        food_info_3 = food_info.filter(classification='3')

        user = request.user
        if user.is_authenticated:
            like = user.userlike_set.filter(like_id=food.article_id)
            if like:
                like_status = 'yes'
            else:
                like_status = 'no'

            fav = user.userfav_set.filter(fav_id=food.article_id)
            if fav:
                fav_status = 'yes'
            else:
                fav_status = 'no'
        else:
            like_status = 'unsigned'
            fav_status = 'unsigned'

        return render(request, 'food/food_article.html', {
            "food": food,
            "food_image": food_image,
            "food_steps": food_steps,
            "food_info_1": food_info_1,
            "food_info_2": food_info_2,
            "food_info_3": food_info_3,
            "popular_food": popular_food,
            "like_status": like_status,
            "fav_status": fav_status,
            "focus": "article",
        })


class TagFoodView(View):

    def get(self, request, tag):

        food_tag = Tags.objects.get(name=tag)
        food_articles = food_tag.foodarticle_set.order_by("-like")
        popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        paginator = Paginator(food_articles, 12, request=request)
        food_list_page = paginator.page(page)

        return render(request, 'food/food_ranking.html', {
            "food_list": food_list_page,
            "popular_food": popular_food,
            "message": True,
            "focus": "article",
        })


class FoodImageRankView(View):

    def get(self, request):
        food_image = FoodImage.objects.order_by('-fav')
        popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

        message = bool(food_image)

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        paginator = Paginator(food_image, 20, request=request)
        image_list = paginator.page(page)

        return render(request, "food/food_image_rank.html", {
            "image_list": image_list,
            "popular_food": popular_food,
            "message": message,
            "focus": "image",
        })


class SingleFoodImageView(View):

    def get(self, request, image_id):

        image = FoodImage.objects.get(name=image_id)
        image.click_number += 1
        image.save()

        # path = os.path.split(str(image.image))[0]
        path = '/'.join(image.image.url.split('/')[2:-1])
        image.image = os.path.join(path, f'{image.name}-full.jpg')

        popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

        user = request.user
        if user.is_authenticated:
            like = user.userlike_set.filter(like_id=image.name)
            if like:
                like_status = 'yes'
            else:
                like_status = 'no'

            fav = user.userfav_set.filter(fav_id=image.name)
            if fav:
                fav_status = 'yes'
            else:
                fav_status = 'no'
        else:
            like_status = 'unsigned'
            fav_status = 'unsigned'

        return render(request, "food/food_image.html", {
            'image': image,
            "popular_food": popular_food,
            "like_status": like_status,
            "fav_status": fav_status,
            "focus": "image",
        })


class TagImageView(View):

    def get(self, request, tag):

        image_tag = ImageTags.objects.get(name=tag)
        images = image_tag.foodimage_set.order_by("-like")
        popular_food = FoodArticle.objects.order_by("-fav")[:3]

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        paginator = Paginator(images, 12, request=request)
        image_list = paginator.page(page)

        return render(request, 'food/food_image_rank.html', {
            "image_list": image_list,
            "popular_food": popular_food,
            "message": True,
            "focus": "image",
        })


class SearchView(View):

    def get(self, request):

        keyword = request.GET.get('keyword', "")
        search_type = request.GET.get('type', "")

        if search_type == "Food Articles":  # XXX
            search_food_article = FoodArticle.objects.filter(
                Q(tags__name__icontains=keyword) |
                Q(ingredient_list__icontains=keyword) |
                Q(name__icontains=keyword)
            ).distinct().order_by('-fav')

            popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

            message = bool(search_food_article)

            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1
            paginator = Paginator(search_food_article, 20, request=request)
            food_article_list = paginator.page(page)

            return render(request, "food/food_ranking.html", {
                "food_list": food_article_list,
                "popular_food": popular_food,
                "message": message,
                "focus": "article",
            })

        else:
            search_food_image = FoodImage.objects.filter(
                tags__name__icontains=keyword
            ).distinct().order_by('-fav')

            popular_food = FoodArticle.objects.all().order_by("-fav")[:3]

            message = bool(search_food_image)

            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1
            paginator = Paginator(search_food_image, 20, request=request)
            image_list = paginator.page(page)

            return render(request, "food/food_image_rank.html", {
                "image_list": image_list,
                "popular_food": popular_food,
                "message": message,
                "focus": "image",
            })


# Data dump function
def data_transform():
    """
    Dump the data in mongodb to the PostgresSQL database.
    The main purpose is to dump the data in the leaderboard,
    because the numbers of likes and favorites of the food are not crawled,
    it is randomly generated through the dump
    """
    conn = mongo_client()
    data = conn.food.food_rank.find({}).batch_size(30)
    for item in data:
        food_article = FoodArticle()
        food_article.article_id = item["random_id"]
        food_article.name = item["name"]
        food_article.image = item["image_path"]
        food_article.author = item["author"]
        food_article.ingredient_list = item["ingredient_list"]
        food_article.count = item["count"]
        # Get the score of the article,
        # extract documents from the food_data collection
        evaluation_tag_conn = mongo_client()
        evaluation_tag = evaluation_tag_conn.food.food_data.find_one({
            "random_id": item["random_id"]
        })
        food_article.like = evaluation_tag["evaluation"]['like']
        food_article.fav = evaluation_tag["evaluation"]['fav']
        food_article.click_number = random.randint(2000, 5000)
        food_article.save()
    conn.close()


# ManyToMany
def add_article_tags():
    conn = mongo_client()
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        food_article = FoodArticle.objects.get(article_id=item['random_id'])
        for tag in item['tags_list']:
            food_tag = Tags.objects.get(name=tag)
            food_article.tags.add(food_tag)
        food_article.save()
    conn.close()


def get_tags():
    conn = mongo_client()
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        for tag in item["tags_list"]:
            if not Tags.objects.filter(name=tag):
                Tags.objects.create(name=tag)
    conn.close()


def get_steps():
    conn = mongo_client()
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        for step in item["steps_list"]:
            food_step = FoodSteps()
            article = FoodArticle.objects.get(article_id=item["random_id"])
            # This must be an instance of FoodArticle
            # to establish a one-to-many association
            # Using item["random_id"] directly will result in an error
            food_step.article_id = article
            food_step.step_number = step["step_number"]
            food_step.image = step['step_image_path']
            food_step.description = step['step_info']
            food_step.save()


# Reduce the size of the picture and save it to the PostgresSQL database
def resize_image():
    """Food Picture Processing Function"""
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        path = os.path.join(BASE_DIR, "media", 'food_image', item['random_id'])
        full_image = Image.open(os.path.join(path, f'{item["random_id"]}-full.jpg'))
        (x, y) = full_image.size
        new_x = 480
        new_y = int(y * new_x / x)
        small_image = full_image.resize((new_x, new_y), Image.ANTIALIAS)
        if small_image.mode != "RGB":
            small_image = small_image.convert("RGB")
        small_image.save(os.path.join(path, f'{item["random_id"]}-small.jpg'))
        full_image.close()
    conn.close()


def image_transform():
    """Dump image data from MongoDB to PostgresSQL"""
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        for tag in item["tags_list"]:
            if not ImageTags.objects.filter(name=tag):
                ImageTags.objects.create(name=tag)
        image = FoodImage()
        image.name = item["random_id"]
        image.image = os.path.join('food_image', item['random_id'], f'{item["random_id"]}-small.jpg')
        image.save()
    conn.close()


def add_image_tags():
    """Add label data to the picture"""
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        image = FoodImage.objects.get(name=item['random_id'])
        for tag in item["tags_list"]:
            image_tag = ImageTags.objects.get(name=tag)
            image.tags.add(image_tag)
        image.save()
    conn.close()


def delete_error_image():
    """Delete wrong picture data"""
    import shutil

    path = os.path.join(BASE_DIR, 'media', 'food_image')
    wrong_set = {name for name in os.listdir(path)}
    right_set = set()
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        right_set.add(item["random_id"])
    conn.close()
    diff = wrong_set - right_set
    print(len(diff))
    for name in diff:
        shutil.rmtree(os.path.join(path, name))


# Modify the number of likes, favorites and clicks of the picture
def image_like():
    """
    Random data cannot be defined in the model.
    The program will be compiled directly at runtime,
    resulting in all random data being the same.
    """
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        image = FoodImage.objects.get(name=item["random_id"])
        image.like = random.randint(200, 500)
        image.fav = random.randint(500, 2000)
        image.click_number = random.randint(2000, 5000)
        image.save()
    conn.close()


def image_transform_1():
    conn = mongo_client()
    data = conn.food.food_image.find({}).batch_size(30)
    for item in data:
        image = FoodImage.objects.get(name=item["random_id"])
        image.image = os.path.join('food_image', item['random_id'], f'{item["random_id"]}-small.jpg')
        image.save()
    conn.close()


# In order to enable users to upload article data,
# the data originally stored in MongoDB needs to be dumped to PostgresSQL
def food_data_transform():
    conn = mongo_client()
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        for ingredient in item['ingredients_list']:
            for key, value in ingredient['formulas'].items():
                food = FoodArticle.objects.get(article_id=item['random_id'])
                food_in = FoodIngredients()
                food_in.article_id = food
                if ingredient['name'] == 'Main ingredient':  # XXX
                    key_name = '1'
                elif ingredient['name'] == 'Supplementary ingredient': # XXX
                    key_name = '2'
                else:
                    key_name = '3'
                food_in.name = key
                food_in.dosage = value
                food_in.classification = key_name
                food_in.save()
    conn.close()


def food_data_transform_1():
    conn = mongo_client()
    data = conn.food.food_data.find({}).batch_size(30)
    for item in data:
        food = FoodArticle.objects.get(article_id=item['random_id'])
        food.description = item['desc']
        food.tips = item['tip_info']
        food.save()
    conn.close()
