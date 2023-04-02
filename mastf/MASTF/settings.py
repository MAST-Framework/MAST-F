"""
Django settings for MASTF project.
Generated by 'django-admin startproject' using Django 4.1.7.
For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
import logging

from pathlib import Path

logger = logging.getLogger(__name__)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vgh0!k)t1(4$5gb+f*g#$&lqwx6k%dp+d!x8v%jh1ct9%y=q+a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600 # 1h
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mastf.MASTF',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

ROOT_URLCONF = 'mastf.MASTF.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
  os.path.join(BASE_DIR, 'static'),
)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

WSGI_APPLICATION = 'mastf.MASTF.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler"
]


CELERY_RESULT_BACKEND = 'django-db'
# CELERY_TASK_TIME_LIMIT = 30 * 60

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -!- START MASTF-CONFIG -!-
MASTF_PASSWD_MIN_LEN = 12
MASTF_USERNAME_MIN_LEN = 5
# -!- END MASTF-CONFIG -!-


# -!- START USER-CONFIG -!-

PROJECTS_ROOT = BASE_DIR / "projects"
if not PROJECTS_ROOT.exists():
    PROJECTS_ROOT.mkdir()

DEBUG_HTML = True
API_ONLY = False



PROJECTS_TABLE_COLUMNS = [
    "ID", # the project's ID won't be visible directly
    "Project Name",
    "Last Scan Origin",
    "Last Scan",
    "Tags",
    "Groups",
    "Risk Level",
    "High",
    "Medium",
    "Low",
    # Uncomment the next line to be able to see SECURE results
    # "Secure",
]

APPS_TABLE_COLUMNS = [
    "Name", # No ID, just name
    "Tags",
    "Risk Level",
    "Projects",
    "High",
    "Medium",
    "Low",
    # Uncomment the next line to be able to see SECURE results
    # "Secure",
]

# -!- END USER-CONFIG -!-

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(asctime)-15s - %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'color': {
            '()': 'colorlog.ColoredFormatter',
            'format':
                '%(log_color)s[%(levelname)s] %(asctime)-15s - %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'color',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console', 'logfile'],
            # DEBUG will log all queries, so change it to WARNING.
            'level': 'INFO',
            'propagate': False,   # Don't propagate to other handlers
        },
        'mastf.MASTF': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
    },
}
