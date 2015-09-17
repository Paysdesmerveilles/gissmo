from gissmo.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

SECRET_KEY = '%%p8v8k44rd8hw%_j%m3hrzg6w^1eic6x6g28nqdn&4=qtelok'

ROOT_URLCONF = 'gissmo.urls.dev'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_NAME', 'gissmo_dev'),
        'USER': os.getenv('POSTGRES_USER', 'gissmo'),
        'PASSWORD': os.getenv('POSTGRES_PASS', 'gissmo'),
        'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

INSTALLED_APPS += (
    'django_extensions',
)
