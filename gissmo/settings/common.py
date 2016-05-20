from __future__ import unicode_literals
import os

DEBUG = True

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB', 'postgres'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASS', 'postgres'),
        'HOST': os.getenv('DB_PORT_5432_TCP_ADDR', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT_5432_TCP_PORT', '5432'),
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False
USE_L10N = True

USE_TZ = True

UPLOAD_ROOT = os.path.join(os.path.abspath(os.path.curdir), 'upload')
if os.getenv('UPLOAD_ROOT', None) is not None:
    UPLOAD_ROOT = os.path.abspath(os.getenv('UPLOAD_ROOT'))

MEDIA_ROOT = os.path.join(os.path.abspath(os.path.curdir), 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(os.path.abspath(os.path.curdir), 'static')
if os.getenv('STATIC_ROOT', None) is not None:
    STATIC_ROOT = os.path.abspath(os.getenv('STATIC_ROOT'))
STATIC_URL = '/gissmo/static/'

# Additional locations of static files
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

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

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'gissmo.wsgi.application'

INSTALLED_APPS = (
    'flat',
    'autocomplete_light',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework',
    'equipment',
    'station',
    'gissmo',
    'api',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

REST_FRAMEWORK = {
    # This permission class allow only listed IP in API_ALLOWED_HOSTS.
    # 'DEFAULT_PERMISSION_CLASSES': ('gissmo.permissions.WhitelistPermission',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'UNICODE_JSON': True,
}

# List of allowed IP that can make raquests on REST_FRAMEWORK_API
API_ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '130.79.9.145',  # thefroid.u-strasbg.fr (Olivier DOSSMANN)
    '130.79.10.231',  # gavrinis.u-strasbg.fr (Maxime BES-DE-BERC)
]
