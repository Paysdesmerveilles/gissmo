# Development environment

## With docker-compose

### Prerequisites

You need **Docker** and **docker-compose**.

Cf. http://docs.docker.com/installation/ubuntulinux/

and

Cf. https://docs.docker.com/compose/install/

### Quick setup

With docker-compose you only need to build image, build container, deploy models
and run the server:

```bash
docker-compose build
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py createsuperuser
docker-compose run --rm --service-ports web
```

It will launch the server on the current terminal.

To stop the server, press Ctrl+C.

To stop the database, just do:

    docker-compose stop db

And it will stop our DB.

### Access the GISSMO application

GISSMO is available here: http://localhost:8000/gissmo/ .

## With virtualenv

### Clone the repository

Get the source code and create a virtual environment :
```bash
apt-get install libpq-dev python3-dev virtualenvwrapper git-core python-pip
git clone git@github.com:eost/gissmo.git
(or your fork repos if you tend to contribute)
cd gissmo
mkvirtualenv gissmo
pip install -r requirements.txt
```

### Database server

By default, Gissmo expects a PostGreSQL database named "gissmo" and an user "gissmo" with the password "gissmo" :
```bash
sudo apt-get install postgresql
sudo -u postgres createuser -E -P gissmo
(enter "gissmo" as password)
sudo -u postgres createdb -O gissmo gissmo
./manage syncdb
(create a superuser)
```

### Launch a test instance

Start the test server using this command:
```bash
./manage runserver
```

Open this following url : [http://127.0.0.1/gissmo]() using your superuser account. Finally submit your pull request ;)

## Check its code with flake8

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

## Functional tests

### Prerequisites

As previously with docker-compose:

  * docker
  * docker-compose

### Prepare test environment

**WARNING**: As autocomplete module use static files to work, we need to
collect them.

So first do:

```bash
mkdir static
python manage.py collectstatic --noinput --clear -v 1
```

Then do:

```bash
docker-compose start db
```


### Run functional tests

Then launch functional tests **in a virtualenv** (as previously explained):

```bash
cd gissmo
source bin/activate
pip install -r requirements
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

# Production environment

To use the production environment, you need Docker and docker-compose. We assume you have a copy of Gissmo DB named **gissmo-1.dump**.

Then add the new SECRET\_KEY in **production.env** file.

Finally, do:

```bash
docker-compose -f production.yml build
docker-compose -f production.yml up
PGHOST=localhost PGPORT=5433 PGUSER=gissmo pg_restore -d gissmo gissmo-1.dump
# password is gissmo
# stop them with Ctrl + C
docker-compose -f production.yml run --rm pweb python manage.py migrate admin 0001_initial --fake
docker-compose -f production.yml run --rm pweb python manage.py migrate auth
docker-compose -f production.yml run --rm pweb python manage.py migrate sessions 0001_initial --fake
docker-compose -f production.yml run --rm pweb python manage.py migrate gissmo 0001_initial --fake
docker-compose -f production.yml run --rm pweb python manage.py migrate gissmo
```

You can then create a new superuser as this:

```bash
docker-compose -f production.yml run --rm pweb python manage.py createsuperuser
```

And launch service like this:

```bash
docker-compose -f production.yml run --rm --service-ports pweb
```

**Note**: By default the Dockerfile use this port: **8000**.

# Contributors

* [Olivier Dossmann](https://github.com/blankoworld)
* [Fabien Engels](https://github.com/fabienengels)
* [Martin Dutil](https://github.com/mdutil)

