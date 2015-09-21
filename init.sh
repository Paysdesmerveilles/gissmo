#!/usr/bin/env bash
#
# Start postgreSQL and syncDB
#
# WARNING: USE THIS ONLY INTO A DOCKER INSTANCE

service postgresql start && python manage.py migrate && \
  python manage.py loaddata --app gissmo initial_data && \
  python manage.py createsuperuser
