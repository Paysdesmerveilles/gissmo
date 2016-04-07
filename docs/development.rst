Developer's guide
*****************

Welcome to this developer area where you will find tip & tricks, but especially information about how to improve Gissmo.

Overview
========

Gissmo get priority to **Docker** in order to get an instance of Django.

We use a **Github repository** (https://github.com/eost/gissmo) with a checking code script using **flake8** (Cf. https://github.com/eost/gissmo/blob/master/scripts/git_hooks/pre-commit).

Tests are done on a **python virtual environment** (python-virtualenv).

Documentation use **Sphinx** using **reStructuredText format**.

Bugs and improvements are located here: https://github.com/eost/gissmo/issues/.

Check code with flake8
======================

We consider that:

  * you got Gissmo github source code
  * you created a python virtual environment

In order Git to check code before each commit, use **scripts/git_hooks/pre-commit** script:

.. code-block:: bash

   cp scripts/git_hooks/pre-commit .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit

Then commit (Python virtual environment should be activated). This will check the code and display potential errors.

Link a virtualenv with a postgreSQL container
=============================================

If you have a postgreSQL container, and Gissmo in a Python virtualenv, use **DB_PORT_5432_TCP_PORT** environment variable with **docker inspect** command to launch Django:

.. code-block:: bash

   DB_PORT_5432_TCP_PORT=`docker inspect -f '{{ (index (index .NetworkSettings.Ports "5432/tcp") 0).HostPort}}' gissmo_db` python manage.py runserver

where **gissmo_db** is your database container name and **5432/tcp** is your postgreSQL container hosted port.

Run tests
=========

To run tests:

  * create a postgreSQL container called **gissmo_db** using Docker
  * enter Gissmo source code with a Python virtualenv in which you install Gissmo python dependencies (using *pip install -r requirements*)

Then launch this command (available in Gissmo source code):

.. code-block:: bash

   ./scripts/launch-tests.sh app_name

where **app_name** is the application name you want to test.

For an example we have:

  * **functional_tests**: to launch some functional tests using Firefox
  * **gissmo**: to launch non-graphical tests

**Tip**: You can also launch a specific test using this syntax:

.. code-block:: bash

   ./scripts/launch-tests.sh app_name.NamedClass.test_method_name

for an example:

.. code-block:: bash

   ./scripts/launch-tests.sh functional_tests.tests.ProjectTest.test_project_creation

Generate documentation
======================

Enter into a python virtualenv. Then go to Gissmo source code and do:

.. code-block:: bash

   cd docs
   pip install -r requirements
   make html

Documentation is now located in **_build** directory.

One Docker, 3 ways
==================

As Docker container starts using a specific entrypoint, it delivers 3 possibilities:

  * (default) **production**: start a uWSGI server
  * **test**: start a uWSGI server with DEBUG=True to display errors
  * **development**: start the Django python webserver

**production** mode needs a SECRET_KEY environment variable to work well.

To launch the Docker container using one of these 3 ways, just do:

.. code-block:: bash

   docker run -it --rm -P --link gissmo_db:db -v /srv/upload:/opt/gissmo/upload fabienengels/gissmo:1.5 development

where:

  * **gissmo_db** is your database container name
  * **db** should not be changed
  * **/srv/upload** is your local upload storage directory

You can also launch commands into the Docker container with the **development** version:

.. code-block:: bash

   docker run -it --rm -P --link gissmo_db:db -v /srv/upload:/opt/gissmo/upload gissmo:1.5 development python manage.py migrate

Have fun with Docker containers!

Database migration
==================

**Backup your database first!**

From 1.3 to 1.4
---------------

Just do:

.. code-block:: bash

   docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate admin 0001_initial --fake --noinput
   docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate auth
   docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate sessions 0001_initial --fake
   docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate gissmo 0001_initial --fake
   docker run -it --rm --link gissmo_db:db gissmo:1.4 python manage.py migrate gissmo

**WARNING: New document upload area is located in /opt/gissmo/upload** (in Docker container) so it needs to mount a supplementary volume.

From 1.4 to 1.5:
----------------

Just do:

.. code-block:: bash

   docker run -it --rm --link gissmo_db:db gissmo:1.5 python manage.py migrate gissmo

That's all!
