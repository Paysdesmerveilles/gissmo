#!/usr/bin/env bash
set -e

# DEVELOPEMENT ENVIRONMENT
if [ "$1" = 'development' ]; then
  exec python3 manage.py runserver 0.0.0.0:8000
# PRODUCTION ENVIRONMENT
elif [ "$1" = 'production' ]; then
  export DJANGO_SETTINGS_MODULE=gissmo.settings.production
  exec uwsgi --ini uwsgi.ini --pythonpath $GISSMO_DIR --static-map=/gissmo/static/=$GISSMO_UPLOAD_DIR
# TEST ENVIRONMENT
elif [ "$1" = 'test' ]; then
  export DJANGO_SETTINGS_MODULE=gissmo.settings.production
  export DEBUG=True
  export SECRET_KEY="abcdefghijklmnopqrstuvwxyz"
  exec uwsgi --ini uwsgi.ini --pythonpath $GISSMO_DIR --static-map=/gissmo/static/=$GISSMO_UPLOAD_DIR
fi

exec "$@"
