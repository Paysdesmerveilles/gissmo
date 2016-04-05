# Requirements

You need:

  * docker (Cf. http://docs.docker.com/installation/ubuntulinux/)
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
docker create -v /dbdata:/var/lib/postgresql/data --name dbdata postgres:9.5
docker run -d -P --volumes-from dbdata --name gissmo_db postgres:9.5
```

## Build

Go to gissmo git repository, then:

```bash
docker build -t gissmo:1.5 .
```

## Configure

If you have a previous database that you want to restore, have a look to the *Database migration* chapter of this documentation. Then read *Launch* chapter to know how to launch a Gissmo application with it.

Otherwise you can launch the database creation command like this:

```bash
docker run -it --rm --link gissmo_db:db gissmo:1.5 python manage.py migrate
```

**Note**: We suggest you to create an admin user with this command:

```bash
docker run -it --rm --link gissmo_db:db gissmo python manage.py createsuperuser
```

## Launch

Now you can start Gissmo like this:

```bash
docker run -it --rm -p 8000:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v /srv/upload:/opt/gissmo/upload gissmo:1.5
```

**WARNING**:

  * For Gissmo to work we **need that the link alias is db**. So always name it **db**
  * /opt/gissmo/upload contains all Gissmo uploaded files. Change /srv/upload by your local directory for them

Gissmo is now available, in production mode, at http://127.0.0.1:8000/.

## Ways Docker container works

It gives 3 possibilities:

  * development
  * test
  * production

These words are keywords to launch Docker container in multiple ways. So if you need to launch the test mode, do this:
```bash
docker run -it --rm -p 8000:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v /srv/upload:/opt/gissmo/upload gissmo:1.5 test
```

**By default the production mode is launched**. Which makes an error because you need a SECRET\_KEY variable for it to be used.

### development keyword

Django is launched via ```python manage.py runserver 0.0.0.0:8000``` command.

You're so in development version, with DEBUG=True (you can see errors).

### test keyword

Django is launched using **uwsgi** with DEBUG=True (you can see errors).

A known SECRET\_KEY is used for your application.

### production keyword

Django is launched using **uwsgi** with **DEBUG=False** (Django gives you 404 error pages instead of errors).

You **need to give a SECRET\_KEY** for this mode to work.

For an example:
```bash
docker run -it --rm -P --link gissmo_db:db -e SECRET_KEY="abcdefg" -v /srv/upload:/opt/gissmo/upload gissmo:1.5 production
```

# How to use launch Django into the virtualenv while using Docker postgres container

You need to set DB\_PORT\_5432\_TCP\_PORT variable before. Then just launch Django like this:

```bash
DB_PORT_5432_TCP_PORT=`docker inspect -f '{{ (index (index .NetworkSettings.Ports "5432/tcp") 0).HostPort}}' gissmo_db` python manage.py runserver
```

# Check code with flake8

Copy **scripts/git\_hooks/pre-commit** file to the following: **.git/hooks/pre-commit**.

```bash
cp scripts/git_hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Then use a python virtual environment to commit. It will so check your code.

# Tests

Test server works the same way as the development one.

Just launch the machine like this:

```bash
docker run -it --rm -p 8000:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v /srv/upload:/opt/gissmo/upload gissmo:1.5 test
```

This will launch Django application in uwsgi with DEBUG=True.

## Functional tests

Check that a postgreSQL docker is launched before.

**WARNING**: Autocomplete module use static files to work, so be sure to
collect them.

Do this:

```bash                                                                             
mkdir static                                                                        
python manage.py collectstatic --noinput --clear -v 1                               
```

### Run functional tests

Then launch functional tests **in a virtualenv** (as previously explained):

```bash
cd gissmo_project
source bin/activate
cd gissmo
DB_PORT_5432_TCP_PORT=`docker inspect -f '{{ (index (index .NetworkSettings.Ports "5432/tcp") 0).HostPort}}' gissmo_db` python manage.py test functional_tests
```

or more simply:

```bash
cd gissmo_project
source bin/activate
cd gissmo
./scripts/launch-tests.sh functional_tests
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

**You have to always make a backup before any change. So backup your database first!**

If you have a previous working database, you need to flush it.

Then to migrate database to the given version of Gissmo, follow related explanations.

## From 1.3 to 1.4

Just do:

```bash
docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate admin 0001_initial --fake --noinput
docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate auth
docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate sessions 0001_initial --fake
docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate gissmo 0001_initial --fake
docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate gissmo
```

**WARNING: New document upload area is located in /opt/gissmo/upload** (in Docker container). So it needs to mount a supplementary volume.

## From 1.4 to 1.5

Just do:

```bash
docker run -it --rm --link gissmo_db:db gissmo:1.5 python manage.py migrate gissmo
```

# Contributors

* [Olivier Dossmann](https://github.com/blankoworld)
* [Fabien Engels](https://github.com/fabienengels)
* [Martin Dutil](https://github.com/mdutil)
