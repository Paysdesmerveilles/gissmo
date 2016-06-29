FROM alpine:3.4

MAINTAINER Olivier DOSSMANN, olivier+dockerfile@dossmann.net

ENV GISSMO_DIR /opt/gissmo
ENV UPLOAD_ROOT /data
ENV STATIC_ROOT $GISSMO_DIR/static

COPY . $GISSMO_DIR

WORKDIR $GISSMO_DIR

RUN mkdir -p $GISSMO_DIR/static $UPLOAD_ROOT

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
    chown -R guest:users $GISSMO_DIR $UPLOAD_ROOT && \
    chmod -R 550 $GISSMO_DIR && \
    chmod -R 550 $UPLOAD_ROOT && \
    apk del \
        build-base \
        linux-headers \
        postgresql-dev \
        python3-dev && \
    rm -rf /var/cache/apk/*

VOLUME $UPLOAD_ROOT

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]

EXPOSE 8000
CMD ["production"]
