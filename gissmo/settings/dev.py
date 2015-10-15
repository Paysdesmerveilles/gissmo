from gissmo.settings.common import *  # NOQA
from os import getenv

DEBUG = True

ADMINS = ()
MANAGERS = ADMINS

SECRET_KEY = '%%p8v8k44rd8hw%_j%m3hrzg6w^1eic6x6g28nqdn&4=qtelok'

ROOT_URLCONF = 'gissmo.urls.dev'

INSTALLED_APPS = (
    'gissmo',
    'flat',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'smart_selects',
    # Dev specifics
    'django_extensions',
    'functional_tests',
)

# Update DB settings for docker-compose use
DATABASES['default'].update(
    {
        'HOST': getenv('DB_PORT_5432_TCP_ADDR', '127.0.0.1'),
        'PORT': getenv('DB_PORT_5432_TCP_PORT', '5433'),
    }
)
