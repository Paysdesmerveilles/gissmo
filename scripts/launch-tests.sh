#!/usr/bin/env bash

PROGRAM=`basename $0`

function usage() {
  echo "$PROGRAM app_name... "
  echo -e "  Where app_name... is one or multiple Django application names\n"
  echo -e "EXAMPLE: $PROGRAM functional_tests"
}

if test $# -lt 1; then
  usage
  exit 1
fi

DB_PORT_5432_TCP_PORT=`docker inspect -f '{{ (index (index .NetworkSettings.Ports "5432/tcp") 0).HostPort}}' gissmo_db` python manage.py test $@

exit 0
