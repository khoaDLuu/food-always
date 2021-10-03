"""
Django settings for django_food project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()
# NOTE: Try django-dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# This adds apps to the python sys. Path, can be an import module
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.getenv('DEBUG', False))

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites',

    'apps.user.apps.UserConfig',
    'apps.food.apps.FoodConfig',
    'apps.operation.apps.OperationConfig',

    'xadmin',
    'crispy_forms',
    'reversion',
    'pure_pagination',
    'captcha',

]

AUTH_USER_MODEL = 'user.UserProfiles'

AUTHENTICATION_BACKENDS = [
    'user.views.CustomBackend',
]

LOGIN_URL = '/user/login/'

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_food.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'apps/food/templates'),
            os.path.join(BASE_DIR, 'apps/operation/templates'),
            os.path.join(BASE_DIR, 'apps/user/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # MEDIA_URL, can be used in Templates
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_food.wsgi.application'

# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', ''),
        'USER': os.getenv('DB_USERNAME', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/'),
]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# media path for user-uploaded files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_TSL = os.getenv('EMAIL_HOST_TSL', False)
EMAIL_FROM = os.getenv('EMAIL_FROM', '')


PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 2,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True,
}


# django_simple_captcha - Verification code configuration

CAPTCHA_OUTPUT_FORMAT = '%(text_field)s %(hidden_field)s %(image)s'

CAPTCHA_NOISE_FUNCTIONS = (
    'captcha.helpers.noise_null',  # No style
    # 'captcha.helpers.noise_arcs',  # line
    # 'captcha.helpers.noise_dots',  # point
)

CAPTCHA_IMAGE_SIZE = (125, 50)
CAPTCHA_BACKGROUND_COLOR = '#ffffff'
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
# --> The text contained in images is random letters, such as 'ano5b4'
# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
# --> The text contained in images is a math expression, such as 1 + 2 = ?

CAPTCHA_LENGTH = 4  # The number of characters
CAPTCHA_TIMEOUT = 1  # timeout (minutes)
CAPTCHA_FONT_SIZE = 30  # The font size of characters in a captcha image


# Django Log Settings

BASE_LOG_DIR = os.path.join(BASE_DIR, 'foodalways_log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'error': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'collect': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        # config for the log printed to the terminal
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, 'default.log'),
            'maxBytes': 1024 * 1024 * 100,  # 100M
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'warn': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, 'warn.log'),
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, 'error.log'),
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 5,
            'formatter': 'error',
            'encoding': 'utf-8',
        },
    },

    'loggers': {
        # The default logger application configuration is as follows
        '': {
            'handlers': ['default', 'warn', 'error'],
            'level': 'DEBUG',
            'propagate': True,  # If you have a parent logger, set this to False
        },
        'collect': {
            'handlers': ['console', 'default', 'warn', 'error'],
            'level': 'INFO',
        }
    },
}


# App settings

PROXY_HOST = os.getenv('PROXY_HOST', '')
PROXY_PORT = int(os.getenv('PROXY_PORT', 8282))
PROXY_API_KEY = os.getenv('PROXY_API_KEY', '')
IMAGE_WEBSITE_URL = os.getenv('IMAGE_WEBSITE_URL', '')
FOOD_WEBSITE_AJAX_URL = os.getenv('FOOD_WEBSITE_AJAX_URL', '')
FOOD_WEBSITE_RANKING_URL = os.getenv('FOOD_WEBSITE_RANKING_URL', '')
FOOD_WEBSITE_REFERRER_URL = os.getenv('FOOD_WEBSITE_REFERRER_URL', '')
