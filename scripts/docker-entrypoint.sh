#!/usr/bin/env sh
set -e

if ! [ "$POSTGRES_DB" ]; then
  export POSTGRES_DB="postgres"
fi
if ! [ "$POSTGRES_HOST"] && [ "DB_PORT_5432_TCP_ADDR" ]; then
  export POSTGRES_HOST="$DB_PORT_5432_TCP_ADDR"
else
  export POSTGRES_HOST="127.0.0.1"
fi
if ! [ "$POSTGRES_USER" ]; then
  export POSTGRES_USER="postgres"
fi
if ! [ "$POSTGRES_PORT" ] && [ "DB_PORT_5432_TCP_PORT" ]; then
  export POSTGRES_PORT="$DB_PORT_5432_TCP_PORT"
else
  export POSTGRES_PORT="5432"
fi

# Check /data directory
chmod -R 700 $UPLOAD_ROOT
chown -R guest $UPLOAD_ROOT

# DEVELOPEMENT ENVIRONMENT
if [ "$1" = 'development' ]; then
  exec python3 manage.py runserver 0.0.0.0:8000
# PRODUCTION ENVIRONMENT
elif [ "$1" = 'production' ]; then
  export DJANGO_SETTINGS_MODULE=gissmo.settings.production
  exec uwsgi --ini uwsgi.ini --pythonpath $GISSMO_DIR --static-map=/gissmo/static/=$STATIC_ROOT
# TEST ENVIRONMENT
elif [ "$1" = 'test' ]; then
  export DJANGO_SETTINGS_MODULE=gissmo.settings.production
  export DEBUG=True
  export SECRET_KEY="abcdefghijklmnopqrstuvwxyz"
  exec uwsgi --ini uwsgi.ini --pythonpath $GISSMO_DIR --static-map=/gissmo/static/=$STATIC_ROOT
fi

exec "$@"
