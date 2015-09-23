# Version 0.0
# This Dockerfile creates a fresh environment for Gissmo

FROM debian:jessie

MAINTAINER Olivier DOSSMANN, olivier+dockerfile@dossmann.net

# Main variables
ENV DEBIAN_FRONTEND noninteractive
ENV PG_VERSION 9.4

# Add Strasbourg Debian Mirror list (except security one) to update the Dockerfile faster
RUN echo "deb http://ftp.u-strasbg.fr/debian jessie main" > /etc/apt/sources.list; \
  echo "deb http://ftp.u-strasbg.fr/debian jessie-updates main" >> /etc/apt/sources.list; \
  echo "deb http://security.debian.org jessie/updates main" >> /etc/apt/sources.list; \
  apt-get update; \
  apt-get upgrade -y

# DEPENDANCIES (after an update)
# - postgresql: database
# - libpq-dev python-dev python-pip: for Django
RUN apt-get install -y \
  postgresql-$PG_VERSION \
  libpq-dev \
  python-dev \
#  supervisor \
  python-pip

# GISSMO directory
RUN mkdir -p /opt/gissmo
# Add special user gissmo
RUN useradd -m gissmo # create the home directory (-m option)
RUN echo "gissmo:gissmo" | chpasswd # change default gissmo password

# Install Django dependancies
COPY requirements.txt /opt/gissmo_requirements.txt
# non-resolved issue about distribute into Docker
RUN sed -i '/distribute==/d' /opt/gissmo_requirements.txt
RUN pip install -r /opt/gissmo_requirements.txt

# Configure postgreSQL
USER postgres

RUN service postgresql start && \
  psql --command "CREATE USER gissmo WITH SUPERUSER PASSWORD 'gissmo';" && \
  createdb -O gissmo gissmo

# Enable remote connections for postgreSQL
RUN echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/$PG_VERSION/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/$PG_VERSION/main/postgresql.conf

# Return as admin user
USER root

## Configure services
#COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
## Launch supervisord
#CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Open postgreSQL (5432), Django (8000) port
EXPOSE 5432 8000

# Did you need some access?
VOLUME ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/opt/gissmo"]

WORKDIR /opt/gissmo
ENTRYPOINT ["/bin/bash"]
