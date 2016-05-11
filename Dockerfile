FROM ubuntu:16.04

MAINTAINER Olivier DOSSMANN, olivier+dockerfile@dossmann.net

ENV GISSMO_DIR /opt/gissmo
ENV GISSMO_UPLOAD_DIR /data
ENV GISSMO_STATIC_DIR $GISSMO_DIR/static

COPY . $GISSMO_DIR

WORKDIR $GISSMO_DIR

RUN mkdir -p $GISSMO_DIR/static $GISSMO_UPLOAD_DIR && \
    mv /usr/bin/ischroot /usr/bin/ischroot.original && \
    ln -s /bin/true /usr/bin/ischroot && \
    echo 'force-unsafe-io' | tee /etc/dpkg/dpkg.cfg.d/02apt-speedup && \
    echo 'DPkg::Post-Invoke {"/bin/rm -f /var/cache/apt/archives/*.deb || true";};' | tee /etc/apt/apt.conf.d/no-cache && \
    apt-get update && apt-get dist-upgrade -y --no-install-recommends && apt-get install -y \
        build-essential \
        libpq-dev \
        python3 \
        python3-pip \
        python3-dev && \
    pip3 install -r requirements.txt && \
    python3 manage.py collectstatic --noinput --clear -v 1 && \
    chown -R www-data:www-data $GISSMO_DIR $GISSMO_UPLOAD_DIR && \
    chmod -R 550 $GISSMO_DIR && \
    chmod -R 550 $GISSMO_UPLOAD_DIR && \
    apt-get purge -y python3-pip build-essential && \
    apt-get autoremove -y --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache

VOLUME $GISSMO_UPLOAD_DIR

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]

EXPOSE 8000

CMD ["production"]

USER www-data
