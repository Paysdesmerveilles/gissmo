FROM alpine:edge

MAINTAINER Olivier DOSSMANN, olivier+dockerfile@dossmann.net

ENV GISSMO_DIR /opt/gissmo
ENV GISSMO_UPLOAD_DIR /data
ENV GISSMO_STATIC_DIR $GISSMO_DIR/static

COPY . $GISSMO_DIR

WORKDIR $GISSMO_DIR

RUN mkdir -p $GISSMO_DIR/static $GISSMO_UPLOAD_DIR

RUN apk --no-cache --update add \
        build-base \
        linux-headers \
        libpq \
        postgresql-dev \
        py-configobj \
        python3 \
        python3-dev && \
    python3 -m ensurepip && \
    pip3 install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt && \
    python3 manage.py collectstatic --noinput --clear -v 1 && \
    chown -R guest:users $GISSMO_DIR $GISSMO_UPLOAD_DIR && \
    chmod -R 550 $GISSMO_DIR && \
    chmod -R 550 $GISSMO_UPLOAD_DIR && \
    apk del \
        build-base \
        linux-headers \
        postgresql-dev \
        python3-dev && \
    rm -rf /var/cache/apk/*

VOLUME $GISSMO_UPLOAD_DIR

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]

EXPOSE 8000

CMD ["production"]

USER guest
