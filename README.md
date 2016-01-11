# Requirements

You need:

  * docker (Cf. http://docs.docker.com/installation/ubuntulinux/)
  * [optional] docker-compose (Cf. https://docs.docker.com/compose/install/)
  * python3
  * python-virtualenv
  * python-pip
  * git-core
  * libpq-dev
  * python3-dev

For an example, you can install them on Ubuntu like this:

```bash
sudo apt-get install libpq-dev python3-dev python-virtualenv git-core python3-pip
```

# Installation

A python-virtualenv directory is needed in which you can install all required libraries and the GISSMO project.

To prepare it:

```bash
mkdir gissmo_project/
virtualenv -p python3 gissmo_project
cd gissmo_project
git clone git@github.com:eost/gissmo.git gissmo
cd gissmo
pip install -r requirements.txt
```

# Docker

Gissmo application takes advantage of Docker. There is a **Dockerfile** that permit to launch Gissmo in a Docker container.

But pay attention, you need to launch a postgreSQL Docker container before, then link it to Gissmo Docker.

For an example:

```bash
docker run -it --rm --name postgres postgres -e POSTGRES_USER=gissmo -e POSTGRES_PASSWORD=gissmo
```

## Build

Go to gissmo git repository, then:

```bash
docker build -t gissmo .
```

## Launch

Now you can start Gissmo like this:

```bash
docker run -it --rm -p 8000:8000 --link postgres:db gissmo development
```

Gissmo is now available, in development mode, at http://127.0.0.1:8000/.

## Ways Docker container works

It gives 3 possibilities:

  * development
  * test
  * production

These words are keywords to launch Docker container in multiple ways. So if you need to launch the test mode, do this:
```bash
docker run -it --rm -p 8000:8000 --link postgres:db gissmo test
```

**By default the production mode is launched**. Which makes an error because you need a SECRET_KEY variable for it to be used.

### development keyword

Django is launched via ```python manage.py runserver 0.0.0.0:8000``` command.

You're so in development version, with DEBUG=True (you can see errors).

### test keyword

Django is launched using **uwsgi** with DEBUG=True (you can see errors).

A known SECRET_KEY is used for your application.

### production keyword

Django is launched using **uwsgi** with **DEBUG=False** (Django gives you 404 error pages instead of errors).

You **need to give a SECRET_KEY** for this mode to work.

For an example:
```bash
docker run -it --rm -P 8001 --link postgres:db -e SECRET_KEY="abcdefghijkl" gissmo production
```

# How to use launch Django into the virtualenv while using Docker postgres container

You need to set DB_PORT_5432_TCP_PORT variable before. Then just launch Django like this:

```bash
DB_PORT_5432_TCP_PORT=5433 python manage.py runserver
```

# Check code with flake8

Create the following **.git/hooks/pre-commit** file:

```python
#!/usr/bin/env python

import glob
import os
import sys

site_packages = glob.glob('%s/lib/*/site-packages' % os.environ['VIRTUAL_ENV'])[0]
sys.path.insert(0, site_packages)

from flake8.run import git_hook

COMPLEXITY = os.getenv('FLAKE8_COMPLEXITY', 10)
STRICT = os.getenv('FLAKE8_STRICT', True)
IGNORE = os.getenv('FLAKE8_IGNORE', 'E501')
LAZY = os.getenv('FLAKE8_LAZY', False)

if __name__ == '__main__':
        sys.exit(git_hook(
        complexity=COMPLEXITY,
        strict=STRICT,
        ignore=IGNORE,
        lazy=LAZY,
    ))
```

Change it to an executable one:

```bash
chmod +x .git/hooks/pre-commit
```

Then use a python virtual environment to use it.

# Tests

Test server works the same way as the development one.

Just launch the machine like this (need docker-compose installed):

```bash
docker-compose run --rm --service-ports web test
```

This will launch Django application in uwsgi with DEBUG=True.

## Functional tests

You need only database launched for tests. For an example with docker-compose, you can launch database like this:

```bash
docker-compose start db
```

### Run functional tests

Then launch functional tests **in a virtualenv** (as previously explained):

```bash
cd gissmo_project
source bin/activate
cd gissmo
python manage.py test functional_tests
```

It will launch Firefox and check some URLs.

**TIP**: You can only launch some tests by using this syntax:

```bash
python manage.py test functional_tests.TestClassName
```

for an example:

```bash
python manage.py test functional_tests.ActorTest
```

will launch tests from ActorTest class. This is useful when coding tests.

### Run functional tests on a staging website

You need to know:

  * admin user (**USER**)
  * admin password (**PWD**)
  * staging website URL (**--liveserver**)

Which give us:

```bash
USER=olivier PWD=olivier python manage.py test functional_tests --liveserver=thefroid.u-strasbg.fr:8000
```

# Database migration

## Migration from 1.3 to 1.4

To migrate the database you need:

  * to have a docker postgresql database launched (and know its name)
  * have a dump from your current database

Then, just do this:

```bash
PGHOST=localhost PGPORT=5433 PGUSER=gissmo PGPASSWORD=gissmo pg_restore -d gissmo gissmo-1.dump
docker run -it --rm --link postgres:db gissmo python manage.py migrate admin 0001_initial --fake --noinput
docker run -it --rm --link postgres:db gissmo python manage.py migrate auth
docker run -it --rm --link postgres:db gissmo python manage.py migrate sessions 0001_initial --fake
docker run -it --rm --link postgres:db gissmo python manage.py migrate gissmo 0001_initial --fake
docker run -it --rm --link postgres:db gissmo python manage.py migrate gissmo
```

**WARNING: New document upload area is located in /opt/gissmo/upload** (in Docker container). So it needs to mount a volume.

# Contributors

* [Olivier Dossmann](https://github.com/blankoworld)
* [Fabien Engels](https://github.com/fabienengels)
* [Martin Dutil](https://github.com/mdutil)
