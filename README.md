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
docker-compose run --rm web python manage.py syncdb
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
apt-get install libpq-dev python-dev virtualenvwrapper git-core python-pip
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

# Tests

## Functional tests

### Prerequisites

As previously with docker-compose:

  * docker
  * docker-compose

### Prepare test environment

Just do:

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
