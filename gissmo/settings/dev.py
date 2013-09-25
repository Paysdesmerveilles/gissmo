from gissmo.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

SECRET_KEY = '%%p8v8k44rd8hw%_j%m3hrzg6w^1eic6x6g28nqdn&4=qtelok'

ROOT_URLCONF = 'gissmo.urls.dev'

INSTALLED_APPS += (
    'django_extensions',
)