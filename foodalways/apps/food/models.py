import os
import random
import time

from django.db import models
from django.utils import timezone


def food_article_image_upload_path(instance, filename):
    return os.path.join(
        "food_article",
        instance.article_id,
        filename
    )


def food_article_step_image_upload_path(instance, filename):
    return os.path.join(
        "food_article",
        instance.article_id,
        'step',
        filename
    )


def food_image_upload_path(filename):
    return os.path.join(
        "food_image",
        "%Y/%m",
        filename
    )


def create_random_id():
    stings = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"
    random_string = "".join(random.sample(stings, 8))
    return f'{int(time.time())}-{random_string}'


class Tags(models.Model):
    name = models.CharField(max_length=20, default="", verbose_name="label")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="added at")

    class Meta:
        db_table = "food_tags"
        verbose_name = "Food labels"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class FoodArticle(models.Model):
    article_id = models.CharField(
        max_length=24,
        default=create_random_id,
        verbose_name="article id",
        unique=True
    )
    name = models.CharField(
        max_length=100,
        default="",
        verbose_name="The name of the food",
        db_index=True
    )
    description = models.TextField(verbose_name='food description', default='')
    ingredient_list = models.CharField(
        max_length=200,
        default="",
        verbose_name="Raw material table"
    )
    image = models.ImageField(
        upload_to=food_article_image_upload_path,
        null=True,
        blank=True,
        verbose_name="cover"
    )
    author = models.CharField(
        max_length=100,
        default="",
        verbose_name="author",
        db_index=True
    )
    like = models.IntegerField(default=0, verbose_name="Like count")
    fav = models.IntegerField(default=0, verbose_name="Favorite count")
    click_number = models.IntegerField(default=0, verbose_name="clicks")
    tags = models.ManyToManyField(
        Tags, blank=True, verbose_name="labels", db_index=True
    )
    tips = models.TextField(verbose_name='tips', default='')
    add_time = models.DateTimeField(default=timezone.now, verbose_name="added at")

    class Meta:
        db_table = "food_article"
        verbose_name = "food article"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class FoodIngredients(models.Model):
    article_id = models.ForeignKey(
        FoodArticle,
        on_delete=models.CASCADE,
        to_field="article_id",  # main table's field associated with the foreign key
        db_column="article_id",  # alias for foreign key
        verbose_name='article name'
    )
    name = models.CharField(max_length=50, verbose_name='The name of the ingredients')
    dosage = models.CharField(max_length=20, verbose_name='Food amount')
    classification = models.CharField(
        choices=(
            ('1', 'Main ingredients'),
            ('2', 'Accessories'),
            ('3', 'Ingredients')
        ),
        max_length=10,
        verbose_name='Food classification',
        default='1'
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name="added at")

    class Meta:
        db_table = 'food_ingredients'
        verbose_name = 'Foodstuffs'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class FoodSteps(models.Model):
    """Food preparation steps"""
    article_id = models.ForeignKey(
        FoodArticle,
        on_delete=models.CASCADE,
        to_field="article_id",
        db_column="article_id",
        verbose_name='Article name'
    )
    step_number = models.IntegerField(
        default=0, verbose_name="Prep step sequence number"
    )
    description = models.TextField(
        default='',
        verbose_name="Prep step description"
    )
    image = models.ImageField(
        verbose_name="picture of step",
        upload_to=food_article_step_image_upload_path,
        null=True,
        blank=True
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name="added at")

    class Meta:
        db_table = "food_steps"
        verbose_name = "Food preparation steps"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.description


class ImageTags(models.Model):
    name = models.CharField(max_length=20, default="", verbose_name="Picture tag", db_index=True)
    add_time = models.DateTimeField(default=timezone.now, verbose_name="added at")

    class Meta:
        db_table = "food_imagestags"
        verbose_name = "Picture tag"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class FoodImage(models.Model):
    name = models.CharField(max_length=50, verbose_name='Image name', default=create_random_id, db_index=True)
    image = models.ImageField(
        upload_to=food_image_upload_path,
        blank=True,
        verbose_name="Food picture"
    )
    # Failed to crawl the numbers of likes and favorites, use random numbers

    like = models.IntegerField(default=0, verbose_name="Number of likes")
    fav = models.IntegerField(default=0, verbose_name="number of favorites")
    click_number = models.IntegerField(default=0, verbose_name="clicks")
    tags = models.ManyToManyField(ImageTags, blank=True, verbose_name="Image labels", db_index=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="added at")

    class Meta:
        db_table = "food_images"
        verbose_name = "Food picture"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
