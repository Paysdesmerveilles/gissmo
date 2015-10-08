# Version 0.1
# This Dockerfile creates a fresh environment for Gissmo

FROM python:2.7

MAINTAINER Olivier DOSSMANN, olivier+dockerfile@dossmann.net

# Main variables
ENV PYTHONBUFFERED 1
ENV GISSMO_DIR /opt/gissmo

# GISSMO directory
RUN mkdir -p $GISSMO_DIR
WORKDIR $GISSMO_DIR

# Install Django dependancies
COPY requirements.txt $GISSMO_DIR/requirements.txt
# non-resolved issue about distribute into Docker
RUN sed -i '/distribute==/d' $GISSMO_DIR/requirements.txt
RUN pip install -r $GISSMO_DIR/requirements.txt

# Add current directory code to gissmo project directory
ADD . $GISSMO_DIR

EXPOSE 8000
