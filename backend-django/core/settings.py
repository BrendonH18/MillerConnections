"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from decouple import config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

def determine_environment():
    secret_key_file = os.environ.get('DJANGO_SECRET_KEY')
    if secret_key_file:
        return "Docker"
    else:
        return "Local"
    
environment = determine_environment()

def get_secret(name):
    if environment == "Docker":
        secret_key_file = os.environ.get(name)
        if secret_key_file:
            try:
                with open(secret_key_file) as f:
                    return f.read().strip()
            except IOError:
                raise Exception(f"Secret key file not found: {secret_key_file}")
    elif environment == "Local":
        try:
            return config(name)
        except IOError:
            raise Exception("DJANGO_SECRET_KEY_FILE environment variable not set")
    else:
        raise Exception("Environment not determined")

# def get_secret_key():
#     if environment == "Docker":
#         secret_key_file = os.environ.get('DJANGO_SECRET_KEY')
#         if secret_key_file:
#             try:
#                 with open(secret_key_file) as f:
#                     return f.read().strip()
#             except IOError:
#                 raise Exception(f"Secret key file not found: {secret_key_file}")
#     elif environment == "Local":
#         try:
#             return config('DJANGO_SECRET_KEY')
#         except IOError:
#             raise Exception("DJANGO_SECRET_KEY_FILE environment variable not set")
#     else:
#         raise Exception("Environment not determined")
    
# def get_db_key():
#     secret_key_file = os.environ.get('POSTGRES_PASSWORD')
#     if secret_key_file:
#         try:
#             with open(secret_key_file) as f:
#                 return f.read().strip()
#         except IOError:
#             raise Exception(f"Secret key file not found: {secret_key_file}")
#     else:
#         try:
#             return config('POSTGRES_PASSWORD')
#         except IOError:
#             raise Exception("POSTGRES_PASSWORD environment variable not set")    

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'Users',
    'core',
    'Customers',
    'Appointments'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

AUTH_USER_MODEL = "Users.CustomUser"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db' if environment == "Docker" else 'localhost',
        'PORT': 5432,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

CORS_ALLOWED_ORIGINS = [
    # "http://127.0.0.1:3000",
    # "http://localhost:3000",
    # "http://127.0.0.1:8000",
    # "http://localhost:8000",
    "http://127.0.0.1",
    "http://localhost",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'