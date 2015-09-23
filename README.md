# Development environment

## With Docker

### Prerequisites

Cf. http://docs.docker.com/installation/ubuntulinux/

### Quick setup

```bash
git clone https://github.com/eost/gissmo gissmo
cd gissmo
docker build -t gissmo:latest .
```

Your GISSMO environment is now ready.

**Note**: This could be done with the following command:

```bash
./scripts/docker_build.sh
```

Each time you want to launch a *GISSMO instance*, use this command:

```bash
docker run --rm -it -p :8000 -v `pwd`:/opt/gissmo --name=gissmo gissmo:latest
(then into the docker instance)
```

And you will enter a *GISSMO instance* named **gissmo**.

**Note**: This could be done with the following command:

```bash
./scripts/docker_start.sh
```

### Launch postgreSQL and Django

Into your GISSMO instance, use these commands:

```bash
service postgresql start
./manage syncdb
./manage runserver 0.0.0.0:8080
```

This will offer your Django application on your Docker instance.

**Note**: This could be done with the following command (in gissmo instance):

```bash
./init.sh
./runserver.sh
```

### Access the GISSMO application

Launch firefox like this (from gissmo directory, **outside docker instance**):

```bash
./scripts/firefox.sh
```

This will open *firefox* with the right IP address.

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

Debian-like packages:

  * docker
  * firefox/iceweasel

Python packages:

  * selenium
  * docker-py

### Prepare test environment

Create a new Docker image:

    ./scripts/docker_build.sh

Create an instance:

    ./script/docker_start.sh

Into the instance:

    ./init.sh
    ./runserver.sh

### Run functional tests

Outside the docker instance:

    python functional_tests/tests.py

It will launch Firefox and check some URLs.
