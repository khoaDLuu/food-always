# Generated by Django 2.1 on 2021-10-03 11:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MessageBoard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Message nickname')),
                ('email', models.EmailField(max_length=245, verbose_name='Message email')),
                ('is_user', models.CharField(choices=[('yes', 'yes'), ('no', 'no')], default='yes', max_length=10, verbose_name='Is it a registered user?')),
                ('message', models.TextField(verbose_name='Message content')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='added at')),
            ],
            options={
                'verbose_name': 'Message message',
                'verbose_name_plural': 'Message message',
                'db_table': 'visitor_message',
            },
        ),
        migrations.CreateModel(
            name='UserFav',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fav_id', models.CharField(db_index=True, max_length=30, unique=True, verbose_name='collection id')),
                ('fav_type', models.CharField(choices=[('food_article', 'food article'), ('food_image', 'food picture'), ('food_author', 'food author')], default='food_article', max_length=20, verbose_name='fav type')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='added at')),
            ],
            options={
                'verbose_name': 'User favorite',
                'verbose_name_plural': 'User favorite',
                'db_table': 'user_fav',
            },
        ),
        migrations.CreateModel(
            name='UserLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like_id', models.CharField(db_index=True, max_length=30, unique=True, verbose_name='like id')),
                ('like_type', models.CharField(choices=[('food_article', 'food article'), ('food_image', 'food picture'), ('food_author', 'food author')], default='food_article', max_length=20, verbose_name='like type')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='added at')),
            ],
            options={
                'verbose_name': 'User likes',
                'verbose_name_plural': 'User likes',
                'db_table': 'user_like',
            },
        ),
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('readable', models.CharField(choices=[('unread', 'unread message'), ('read', 'read message')], default='unread', max_length=10, verbose_name='Is it read?')),
                ('message_title', models.CharField(max_length=80, verbose_name='Message subject')),
                ('message_content', models.TextField(default='', verbose_name='Message content')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='added at')),
            ],
            options={
                'verbose_name': 'User Message',
                'verbose_name_plural': 'User Message',
                'db_table': 'user_message',
            },
        ),
    ]