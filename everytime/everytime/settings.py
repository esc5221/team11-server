"""
Django settings for everytime project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

import json
from django.core.exceptions import ImproperlyConfigured

# local과 server의 설정 변수 분리
try :
    with open('everytime/secret.json', 'r') as f:
        secrets = json.loads(f.read())
except :
    secrets = ""

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)
    except TypeError:
        print("everytime/secret.json does not exist")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if "TEAM11_SERVER_ENV" in os.environ :
    print("env : server")
    get_secret("SECRET_KEY")
    DEBUG = False
    ALLOWED_HOSTS = ['127.0.0.1',]
else: 
    print("env : local")
    SECRET_KEY = 'django-insecure-ax5v)%q)d*bl*78y6qw@9pn(=@5r83s5)+%3ufi4%eqf8og^cm'
    DEBUG = True
    ALLOWED_HOSTS = []


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG_TOOLBAR = os.getenv('DEBUG_TOOLBAR') in ('true', 'True')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'emailcode.apps.EmailCodeConfig',
    'university.apps.UniversityConfig',
    'department.apps.DepartmentConfig',
    'user.apps.UserConfig',

    'django.contrib.sites',
    'rest_framework',
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = "waffle.team11@gmail.com"
EMAIL_HOST_PASSWORD = "showmethemoney"
DEFAULT_FROM_MAIL = "waffle.team11"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'everytime.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'everytime.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
if "TEAM11_SERVER_ENV" in os.environ: 
    get_secret("DATABASES")
else: 
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',
            'PORT': 3306,
            'NAME': 'team11_db',
            'USER': 'team11_db_user',
            'PASSWORD': 'secretkey1234',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'user.User'

# https://king-minwook.tistory.com/m/81?category=790110
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}