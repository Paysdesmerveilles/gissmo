from __future__ import unicode_literals
from gissmo.settings.common import *  # NOQA

import sys

DEBUG = True
DISPLAY_SQL = False

ADMINS = ()
MANAGERS = ADMINS

SECRET_KEY = '%%p8v8k44rd8hw%_j%m3hrzg6w^1eic6x6g28nqdn&4=qtelok'

ROOT_URLCONF = 'gissmo.urls.dev'

INSTALLED_APPS += (
    # Dev specifics
    'django_extensions',
    'functional_tests',
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# Add current developer IP (thefroid.u-strasbg.fr) to allowed hosts
API_ALLOWED_HOSTS += [
    '*',
]

if DISPLAY_SQL is True:
    LOGGING['handlers'].update({
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    })

    LOGGING['loggers'].update({
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    })
