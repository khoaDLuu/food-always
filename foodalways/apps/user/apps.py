from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'
    # Define an alias for model
    verbose_name = 'User management'
