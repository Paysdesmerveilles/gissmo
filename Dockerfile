# Version 0.1
# This Dockerfile creates a fresh environment for Gissmo

FROM python:2.7

MAINTAINER Olivier DOSSMANN, olivier+dockerfile@dossmann.net

# Main variables
ENV PYTHONBUFFERED 1
ENV GISSMO_DIR /opt/gissmo
ENV GISSMO_STATIC_DIR $GISSMO_DIR/static

# GISSMO directory
RUN mkdir -p $GISSMO_DIR
RUN mkdir -p $GISSMO_DIR/upload # For upload purpose
WORKDIR $GISSMO_DIR

# Install Django dependancies
COPY requirements.txt $GISSMO_DIR/requirements.txt
RUN pip install -r $GISSMO_DIR/requirements.txt

# Add current directory code to gissmo project directory
ADD . $GISSMO_DIR

# Collect static files
RUN python manage.py collectstatic --noinput --clear -v 1

# Exposed port
EXPOSE 8000

# Install and run uwsgi
RUN apt-get update && \
  apt-get install -y uwsgi

CMD uwsgi --http :8000 --die-on-term --pythonpath $GISSMO_DIR --module gissmo.wsgi:application --master --socket /tmp/gissmo.sock --processes 4 --reload-on-as 512 --enable-threads --static-map=/gissmo/static/=$GISSMO_STATIC_DIR
