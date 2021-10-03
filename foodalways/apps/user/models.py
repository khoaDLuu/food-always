#!/usr/bin/env python3

import os
import json

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
import time


# Define the upload path of the dynamic user picture file
def upload_user_image_path(instance, filename):
    return os.path.join(
        'user',
        instance.username + "_" + str(instance.id),
        'head_portrait',
        filename
    )


# Define the upload path of the verification code image
def recode_image_path(filename):
    return os.path.join(
        'recode_image',
        filename
    )


# Extract the image verification code from the database by number
def get_recode_image(number):
    return RecodeImage.objects.get(recode_number=number)


# Define access to address information
def get_provinces():
    province_list = [(item.pid, item.name) for item in Provinces.objects.all()]
    return province_list


def get_cities(pid):
    city_list = [(item.cid, item.name) for item in Cities.objects.filter(pid=pid)]
    return city_list


def get_regions(pid, cid):
    region_list = [(item.cid, item.name) for item in Regions.objects.filter(pid=pid, cid=cid)]
    return region_list


class UserProfiles(AbstractUser):
    """
    Extend the user model that comes with django, inherited from AbstractUser
    The attributes of AbstractUser are as follows:
    (id, password, last_login, first_name, last_name,
    username, email, is_superuser, is_staff, date_joined, is_alive)
    """

    nick_name = models.CharField(max_length=30, verbose_name="nickname", default="")
    head_portrait = models.ImageField(
        upload_to=upload_user_image_path,
        default='user/default_head_portrait/default.png',
        blank=True,
        verbose_name="Avatar"
    )
    gender = models.CharField(
        choices=(("male", "male"), ("female", "female")),
        default="male",
        verbose_name="Gender",
        max_length=6
    )
    is_author = models.CharField(
        choices=(("yes", "yes"), ("no", "no")),
        default="no",
        verbose_name="This it a food author",
        max_length=6
    )
    birthday = models.DateField(null=True, blank=True, verbose_name="birthday")
    address = models.CharField(max_length=50, verbose_name="region", blank=True, default="")
    signature = models.CharField(max_length=80, verbose_name="signature", blank=True, default="")

    class Meta:
        verbose_name = "User Info"
        verbose_name_plural = verbose_name
        db_table = "user_profiles"

    def __str__(self):
        return self.username

    def get_head_portrait_json(self):
        d = {"head_portrait": str(getattr(self, 'head_portrait'))}
        return json.dumps(d)


# Province: Provinces, City: cities, District: regions
class Provinces(models.Model):
    pid = models.IntegerField(verbose_name="City ID", default=0)
    name = models.CharField(max_length=10, verbose_name="Province", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="Added at")

    class Meta:
        verbose_name = "Province"
        verbose_name_plural = verbose_name
        db_table = "address_provinces"

    def __str__(self):
        return self.name


class Cities(models.Model):
    pid = models.IntegerField(verbose_name="Province number", default=0)
    cid = models.IntegerField(verbose_name="City ID", default=0)
    name = models.CharField(max_length=20, verbose_name="city", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="Added at")

    class Meta:
        verbose_name = "city"
        verbose_name_plural = verbose_name
        db_table = "address_cities"

    def __str__(self):
        return self.name


class Regions(models.Model):
    """For cities that are not set up, directly adjust the lower-level towns to the county level"""
    pid = models.IntegerField(verbose_name="Province Number", default=0)
    cid = models.IntegerField(verbose_name="City ID", default=0)
    rid = models.IntegerField(verbose_name="County Number", default=0)
    name = models.CharField(max_length=20, verbose_name="county", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="Added at")

    class Meta:
        verbose_name = "countyc"
        verbose_name_plural = verbose_name
        db_table = "address_regions"

    def __str__(self):
        return self.name


class EmailVerifyCode(models.Model):
    """
    E-mail verification code
    Set the number of activations to 1
    The time validity of the verification code can be set according to the time sent
    The added date is datetime.datetime.now(), you can use timedelta(seconds=600) as the time difference
    If timezone.now() > send_time, is still within the validity period
    """
    code = models.CharField(max_length=20, verbose_name="E-mail verification code")
    email = models.EmailField(max_length=245, verbose_name="email")
    send_type = models.CharField(
        choices=(('register', 'registration'), ('forget', 'retrieve password'), ('reset_email', 'email reset')),
        max_length=20,
        verbose_name='Verification code type'
    )
    verify_times = models.IntegerField(default=1, verbose_name="The number of times an user can be verified")
    send_time = models.DateTimeField(default=timezone.now, verbose_name='Send time')

    class Meta:
        verbose_name = 'email verification code'
        verbose_name_plural = verbose_name
        db_table = "email_verify_coder"

    def __str__(self):
        return '{0} > ({1})'.format(self.email, self.code)

    def remove_invalid_code(self):
        if self.send_time.timestamp() - time.time() > 600:
            self.delete()


class RecodeImage(models.Model):
    """Image authentication code"""
    recode_image_name = models.CharField(max_length=10, default="", verbose_name="Verification code image name")
    recode_number_a = models.IntegerField(default=0, verbose_name="Verification code number a")
    recode_number_b = models.IntegerField(default=0, verbose_name="Verification code number b")
    recode_image_path = models.ImageField(
        upload_to=recode_image_path,
        verbose_name="Verification code image"
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name="added at")

    class Meta:
        verbose_name = "image verification code"
        verbose_name_plural = verbose_name
        db_table = "recode_image"

    def __str__(self):
        return self.recode_image_name

    def to_json(self):
        """
        Sequence model instance, so that the specific model instance can be jsonized
        Property description:
        a = RecodeImage.objects.get(recode_number="5+8")
        a._meta --> (<django.db.models.fields.AutoField: id>,
                    <django.db.models.fields.CharField: recode_number>,
                    <django.db.models.fields.files.ImageField: recode_image_path>,
                    <django.db.models.fields.DateTimeField: add_time>)
                    This is an iterable object. Through traversal, the name of each field (field.name) is obtained
        getattr(self, attr) --> Get the field value of the model instance
        The ImageField field is stringified using str()
        """

        fields = []
        for field in self._meta.fields:
            fields.append(field.name)

        d = {}
        for attr in fields:
            d[attr] = str(getattr(self, attr))

        return json.dumps(d)
