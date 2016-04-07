Installation with Python virtualenv
***********************************

Recommended way is to :doc:`install Gissmo with Docker<installation_docker>`.

In case you're not comfortable with Docker, the solution is to install Gissmo with a local postgreSQL database and Python virtualenv.

Requirements
============

Gissmo needs:

.. code-block:: bash

   sudo apt-get install libpq-dev python3-dev python-virtualenv python3-pip

.. _postgresql-preparation:

postgreSQL preparation
======================

Install postgreSQL, create a user and a database for Gissmo:

.. code-block:: bash

   sudo apt-get install postgresql
   sudo -u postgres createuser -E -P gissmo_user
   (enter a password, for an example "mot2passe2fou")
   sudo -u postgres createdb -O gissmo_user gissmodb

where:

  * **gissmo_user** is your postgreSQL username for Gissmo database
  * **gissmodb** is your Gissmo database name

Keep in mind username, password and database name for incoming steps.

Virtual environment
===================

Create a new directory for your Gissmo installation and adapt it as a python virtualenv:

.. code-block:: bash

   mkdir project
   virtualenv -p python3 project

This directory will contains:

  * Gissmo (for an example gissmo-1.5 directory)
  * all needed python libraries

**Notes**:

  * Gissmo uses Python 3
  * `Have a look to Virtual Environments chapter in Hitchhiker's guide`_ for more information about Python virtual environments
    
.. _Have a look to Virtual Environments chapter in Hitchhiker's guide: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Get Gissmo
==========

Download Gissmo archive and extract it:

.. code-block:: bash

   cd project
   wget "https://github.com/eost/gissmo/archive/v1.5.tar.gz" -O gissmo.tar.gz
   tar xvf gissmo.tar.gz
   cd gissmo-1.5

You're now ready to configure Gissmo.

Gissmo configuration
====================

We consider that you're located in Gissmo installation directory (called previously *project*).

Enter in Python virtual environment and install needed libraries:

.. code-block:: bash

   source bin/activate
   cd gissmo-1.5
   pip install -r requirements.txt

You can check that Django is present:

.. code-block:: bash

   python manage.py

Which will display a list of commands.

Then check database access (with information you were invited to remember in :ref:`postgresql-preparation`):

.. code-block:: bash

   POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASS="mot2passe2fou" python manage.py dbshell

You will see something like that::

   Type "help" for help.

   gissmodb=> 

To exit type this command then **Enter**::

   \q

And launch database migration:

.. code-block:: bash

    POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASS="mot2passe2fou" python manage.py migrate

Static files
============

In Gissmo installation directory, with virtualenv activated, create static directory and generate static files:

.. code-block:: bash

    mkdir static
    python manage.py collectstatic --noinput --clear -v 1

A list of copied files appears.
  
Launch Gissmo
=============

In production mode, Gissmo application needs a SECRET_KEY. For an example, this one::

   abcdefghijklmnopqrstuvwxyz

For more, see `Django documentation about SECRET_KEY`_.

.. _Django documentation about SECRET_KEY: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SECRET_KEY

We use `uWSGI`_ to deliver Gissmo:

.. _uWSGI: http://uwsgi-docs.readthedocs.org/en/latest/

.. code-block:: bash

   SECRET_KEY="abcdefghijklmnopqrstuvwxyz" DJANGO_SETTINGS_MODULE=gissmo.settings.production POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASS="mot2passe2fou" ../bin/uwsgi --ini uwsgi.ini --pythonpath ./ --static-map=/gissmo/static/=./static

Some explanations:

  * using uWSGI and **gissmo.settings.production** sets Gissmo in its production mode. So no DEBUG information will appears
  * we always need to gives SECRET_KEY in production mode
  * you also need database connection settings with POSTGRES_DB, POSTGRES_USER and POSTGRES_PASS
  * we use Python virtualenv uWSGI (with **../bin/uwsgi**)
  * uWSGI settings are located here: **uwsgi.ini**

This way Gissmo is available here: http://localhost:8000/.

Create superuser
================

Gissmo administration needs an administrator called the **superuser**.

**Note**: Database should be started.

Then:

.. code-block:: bash

    POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASS="mot2passe2fou" python manage.py createsuperuser

Just answer to what appears on the screen.
