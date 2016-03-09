# Version 0.2
# This Dockerfile creates a fresh environment for Gissmo

FROM python:3.4

MAINTAINER Olivier DOSSMANN, olivier+dockerfile@dossmann.net

ENV PYTHONBUFFERED 1
ENV GISSMO_DIR /opt/gissmo
ENV GISSMO_STATIC_DIR $GISSMO_DIR/static

RUN mkdir -p $GISSMO_DIR && \
  mkdir $GISSMO_DIR/static && \
  mkdir $GISSMO_DIR/upload
WORKDIR $GISSMO_DIR

RUN useradd gissmo && \
  echo 'gissmo:gissmo' | chpasswd

COPY requirements.txt $GISSMO_DIR/requirements.txt
RUN pip install -r $GISSMO_DIR/requirements.txt

ADD . $GISSMO_DIR

RUN rm -rf $GISSMO_DIR/uploads/* && \
  chown gissmo:gissmo $GISSMO_DIR -R && \
  chmod 755 $GISSMO_DIR -R

RUN python manage.py collectstatic --noinput --clear -v 1

COPY scripts/docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

VOLUME $GISSMO_DIR/upload

EXPOSE 8000

CMD ["production"]

USER gissmo
