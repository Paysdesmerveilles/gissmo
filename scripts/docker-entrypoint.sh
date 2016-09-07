#!/usr/bin/env sh
set -e

manage () {
  exec python3 manage.py $@
}

# DB_PORT_5432_TCP_ADDR and DB_PORT_5432_TCP_PORT exists if you link this
# container to another one called 'db' (while using --link Docker option).
if [ -z "$POSTGRES_HOST" ] && [ -n "$DB_PORT_5432_TCP_ADDR" ]; then
  export POSTGRES_HOST="$DB_PORT_5432_TCP_ADDR"
fi
if [ -z "$POSTGRES_PORT" ] && [ -n "$DB_PORT_5432_TCP_PORT" ]; then
  export POSTGRES_PORT="$DB_PORT_5432_TCP_PORT"
fi

# Now having pSQL access we create static files.
python3 manage.py collectstatic --noinput --clear -v 0

# Check /data directory
chmod -R 700 $UPLOAD_ROOT
chown -R guest $UPLOAD_ROOT

# DEVELOPEMENT ENVIRONMENT
if [ "$1" = 'development' ]; then
  manage runserver 0.0.0.0:8000
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
# MISCELLANEOUS COMMANDS
elif [ "$1" = 'manage' ]; then
  shift
  manage $@
elif [ "$1" = 'migrate' ]; then
  manage migrate
fi

exec "$@"
