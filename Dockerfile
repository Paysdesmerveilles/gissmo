# Version 0.2
# This Dockerfile creates a fresh environment for Gissmo

FROM python:3.4

MAINTAINER Olivier DOSSMANN, olivier+dockerfile@dossmann.net

# Main variables
ENV PYTHONBUFFERED 1
ENV GISSMO_DIR /opt/gissmo
ENV GISSMO_STATIC_DIR $GISSMO_DIR/static

# Add new GISSMO user
RUN useradd -m gissmo
RUN echo "gissmo:gissmo" | chpasswd

# GISSMO directory
RUN mkdir -p $GISSMO_DIR
RUN mkdir -p $GISSMO_DIR/static # For production purposes
RUN mkdir -p $GISSMO_DIR/upload # For upload purposes
WORKDIR $GISSMO_DIR

# Install Django dependancies
COPY requirements.txt $GISSMO_DIR/requirements.txt
RUN pip install -r $GISSMO_DIR/requirements.txt

# Add current directory code to gissmo project directory
ADD . $GISSMO_DIR

# Collect static files
RUN python manage.py collectstatic --noinput --clear -v 1

COPY scripts/docker-start.sh /

RUN chown gissmo $GISSMO_DIR -R

ENTRYPOINT ["/docker-start.sh"]

EXPOSE 8000

USER gissmo

CMD ["production"]
