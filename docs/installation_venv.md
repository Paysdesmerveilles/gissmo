# Installation with Python virtualenv

We recommend you to [install Gissmo with Docker](installation_docker.md).

In case you're not comfortable with Docker, the solution is to install Gissmo with a local postgreSQL database and a Python virtualenv.

You can also create a postgreSQL database container with Docker and use it with Python virtualenv.

## Requirements

Gissmo needs these packages (example with Ubuntu 14.04):

```bash
sudo apt-get install libpq-dev python3-dev python-virtualenv python3-pip
```

## postgreSQL preparation

Install postgreSQL, create a user and a database for Gissmo:

```bash
sudo apt-get install postgresql
sudo -u postgres createuser -E -P gissmo_user
(enter a password, for an example "mot2passe2fou")
sudo -u postgres createdb -O gissmo_user gissmodb
```

where:

  * **gissmo_user**: Gissmo postgreSQL database username
  * **gissmodb**: Gissmo postgreSQL database name

Keep in mind username, password and database name for incoming steps.

## Virtual environment

Create a new directory for your Gissmo installation and apply python virtualenv on it:

```bash
mkdir project
virtualenv -p python3 project
```

This directory will contains:

  * Gissmo (for an example gissmo-1.7.1 directory)
  * all needed python libraries

**Notes**:

  * Gissmo uses Python 3
  * [Have a look to Virtual Environments chapter in Hitchhiker's guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for more information about Python virtual environments
    
## Get Gissmo

Download Gissmo archive and extract it:

```bash
cd project
wget "https://github.com/eost/gissmo/archive/v1.7.1.tar.gz" -O gissmo.tar.gz
tar xvf gissmo.tar.gz
cd gissmo-1.7.1
```

You're now ready to configure Gissmo.

## Gissmo configuration

We consider that you're located in Gissmo installation directory (we call it *project* previously).

Enter in Python virtual environment and install needed libraries:

```bash
source bin/activate
cd gissmo-1.7.1
pip install -r requirements.txt
```

You can check that Django is present:

```bash
python manage.py
```

Which will display a list of commands.

Then check database access (with information you were invited to remember in [postgreSQL preparation](#postgresql-preparation)):

```bash
POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASSWORD="mot2passe2fou" python manage.py dbshell
```

You will see something like that:

```
Type "help" for help.

gissmodb=> 
```

To exit type this command then **Enter**:

```
\q
```

And launch database migration:

```bash
POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASSWORD="mot2passe2fou" python manage.py migrate
```

## Static files

In Gissmo installation directory, with virtualenv activated, create static directory and generate static files:

```bash
mkdir static
python manage.py collectstatic --noinput --clear -v 1
```

A list of copied files appears.
  
## Launch Gissmo

In production mode, Gissmo application needs a SECRET_KEY. For an example, this one:

```
abcdefghijklmnopqrstuvwxyz
```

For more, see [Django documentation about SECRET_KEY](https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SECRET_KEY).

We use [uWSGI](http://uwsgi-docs.readthedocs.org/en/latest/) to deliver Gissmo:

```bash
SECRET_KEY="abcdefghijklmnopqrstuvwxyz" DJANGO_SETTINGS_MODULE=gissmo.settings.production POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASSWORD="mot2passe2fou" ../bin/uwsgi --ini uwsgi.ini --pythonpath ./ --static-map=/gissmo/static/=./static
```

Some explanations:

  * using uWSGI and **gissmo.settings.production** sets Gissmo in its production mode. So no DEBUG information will appears
  * we always need to gives SECRET_KEY in production mode
  * you also need database connection settings with POSTGRES_DB, POSTGRES_USER and POSTGRES_PASSWORD
  * we use Python virtualenv uWSGI (with **../bin/uwsgi**)
  * uWSGI settings are located here: **uwsgi.ini**

This way Gissmo is available here: [http://localhost:8000/](http://localhost:8000/).

## Create superuser via virtualenv

Gissmo administration needs an administrator called the **superuser**.

**Note**: Database should be started.

Then:

```bash
POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASSWORD="mot2passe2fou" python manage.py createsuperuser
```

Just answer to what appears on the screen.
