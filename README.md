# Development environment

## With docker-compose

### Prerequisites

You need **Docker** and **docker-compose**.

Cf. http://docs.docker.com/installation/ubuntulinux/

and

Cf. https://docs.docker.com/compose/install/

### Quick setup

With docker-compose you only need to build containers, deploy models and
run the server:

```bash
docker-compose build web
docker-compose run web python manage.py syncdb
docker-compose run
```

### Access the GISSMO application

GISSMO is available here: http://localhost:8000/

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
