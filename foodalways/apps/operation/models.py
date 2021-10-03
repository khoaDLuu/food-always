
from django.db import models
from django.utils import timezone

from user.models import UserProfiles


class UserLike(models.Model):
    user = models.ForeignKey(
        UserProfiles,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='username',
        verbose_name='User'
    )
    like_id = models.CharField(max_length=30, verbose_name='like id', db_index=True, unique=True)
    like_type = models.CharField(
        choices=(
            ('food_article', 'food article'),
            ('food_image', 'food picture'),
            ('food_author', 'food author')
        ),
        max_length=20,
        verbose_name='like type',
        default='food_article'
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name='added at')

    class Meta:
        db_table = 'user_like'
        verbose_name = 'User likes'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.like_id


class UserFav(models.Model):
    user = models.ForeignKey(
        UserProfiles,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='username',
        verbose_name='User'
    )
    fav_id = models.CharField(max_length=30, verbose_name='collection id', db_index=True, unique=True)
    fav_type = models.CharField(
        choices=(
            ('food_article', 'food article'),
            ('food_image', 'food picture'),
            ('food_author', 'food author')
        ),
        max_length=20,
        verbose_name='fav type',
        default='food_article'
    )
    add_time = models.DateTimeField(default=timezone.now, verbose_name='added at')

    class Meta:
        db_table = 'user_fav'
        verbose_name = 'User favorite'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.fav_id


class UserMessage(models.Model):
    user = models.ForeignKey(
        UserProfiles,
        on_delete=models.CASCADE,
        to_field='username',
        db_column='username',
        verbose_name='The user'
    )
    readable = models.CharField(
        choices=(('unread', 'unread message'), ('read', 'read message')),
        max_length=10,
        verbose_name='Is it read?',
        default='unread'
    )
    message_title = models.CharField(max_length=80, verbose_name='Message subject')
    message_content = models.TextField(default='', verbose_name='Message content')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='added at')

    class Meta:
        db_table = 'user_message'
        verbose_name = 'User Message'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.message_title


class MessageBoard(models.Model):
    name = models.CharField(max_length=20, verbose_name='Message nickname')
    email = models.EmailField(max_length=245, verbose_name='Message email')
    is_user = models.CharField(
        max_length=10,
        choices=(('yes', 'yes'), ('no', 'no')),
        default='yes',
        verbose_name='Is it a registered user?')
    message = models.TextField(verbose_name='Message content')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='added at')

    class Meta:
        db_table = 'visitor_message'
        verbose_name = 'Message message'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
