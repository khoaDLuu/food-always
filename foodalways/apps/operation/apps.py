from django.apps import AppConfig


class OperationConfig(AppConfig):
    name = 'operation'
    # Define an alias for model
    verbose_name = 'The user action'
