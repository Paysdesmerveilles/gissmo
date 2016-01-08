from __future__ import unicode_literals
import os
from gissmo.settings.common import *  # NOQA

DEBUG = os.getenv('DEBUG', False)

ADMINS = (
    ('Fabien Engels', 'fabien.engels@unistra.fr'),
    ('Marc Grunberg', 'marc.grunberg@unistra.fr')
)

SECRET_KEY = os.getenv('SECRET_KEY')

ROOT_URLCONF = 'gissmo.urls.production'

ALLOWED_HOSTS = ['*']
