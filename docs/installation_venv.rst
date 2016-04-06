Installation using Python virtualenv
************************************

Best way is to :doc:`install Gissmo with Docker<installation_docker>`.

In case you're not comfortable with Docker, the solution is to install Gissmo with a postgreSQL database and Python virtualenv (current documentation).

postgreSQL preparation
======================

You have to install postgreSQL, create a user and a database for Gissmo.

Just do:

.. code-block:: bash

   sudo apt-get install postgresql
   sudo -u postgres createuser -E -P gissmo_user
   (enter a password, for an example "mot2passe2fou")
   sudo -u postgres createdb -O gissmo_user gissmodb

where:

  * **gissmo_user** is your postgreSQL username for Gissmo database
  * **gissmodb** is your Gissmo database name

Keep in mind username, password and database name for next steps.

Virtual environment
===================

Install python-virtualenv package, create a new directory and change it as python virtualenv area:

.. code-block:: bash

   sudo apt-get install python-virtualenv
   mkdir project
   virtualenv -p python3 project

This directory will include all needed python libraries and Gissmo directory.

Get Gissmo files
================

We fetch Gissmo files and extract them:

.. code-block:: bash

   cd project
   wget "https://github.com/eost/gissmo/archive/v1.5.tar.gz" -O gissmo.tar.gz
   tar xvf gissmo.tar.gz
   cd gissmo-1.5

You're now ready to start Gissmo configuration.

Gissmo configuration
====================

We consider that you're in Gissmo environement directory (called *project*).

Enter in Python virtual environment and install needed libraries:

.. code-block:: bash

   source bin/activate
   cd gissmo-1.5
   pip install -r requirements.txt

You can check that Django is present with this command:

.. code-block:: bash

   python manage.py

This will display a list of commands.

Then check database access:

.. code-block:: bash

   POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASS="mot2passe2fou" python manage.py dbshell

You will see something like that::

   Type "help" for help.

   gissmodb=> 

Type this to exit the shell (then **Enter**)::

   \q

And launch database migration:

.. code-block:: bash

    POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASS="mot2passe2fou" python manage.py migrate

Prepare static files directory
==============================

Just do this (we consider that you're in Gissmo directory with virtualenv activated):

.. code-block:: bash

    mkdir static
    python manage.py collectstatic --noinput --clear -v 1

A list of copied files appears.
  
Launch Gissmo
=============

You need a SECRET_KEY for your Gissmo application. For an example::

   abcdefghijklmnopqrstuvwxyz

For more, see `Django documentation about SECRET_KEY`_.

.. _Django documentation about SECRET_KEY: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SECRET_KEY

We use `uWSGI`_ to deliver Gissmo on the web:

.. _uWSGI: http://uwsgi-docs.readthedocs.org/en/latest/

.. code-block:: bash

   SECRET_KEY="abcdefghijklmnopqrstuvwxyz" DJANGO_SETTINGS_MODULE=gissmo.settings.production POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASS="mot2passe2fou" ../bin/uwsgi --ini uwsgi.ini --pythonpath ./ --static-map=/gissmo/static/=./static

Some explanations:

  * using uWSGI and **gissmo.settings.production** set Gissmo in its production mode. So no DEBUG information will appears
  * we always need to gives SECRET_KEY in production mode
  * you also need database connection settings with POSTGRES_DB, POSTGRES_USER and POSTGRES_PASS
  * we use Python virtualenv uWSGI (with **../bin/uwsgi**)
  * uWSGI settings are located here: **uwsgi.ini**

This way Gissmo is available here: http://localhost:8000/.

Create superuser
================

Gissmo administration needs an administrator called the **superuser**. So create it.

Database should be started.

Then:

.. code-block:: bash

    POSTGRES_DB=gissmodb POSTGRES_USER=gissmo_user POSTGRES_PASS="mot2passe2fou" python manage.py createsuperuser

Just answer to what appears on the screen.
