Installation with Docker
************************

`Docker`_ makes it easy to deliver applications in something called a **container**. Which have been used to distribute GISSMO.

`Install Docker`_ first (link for a Linux installation).

.. _Docker: https://www.docker.com/
.. _Install Docker: https://docs.docker.com/linux/step_one/

How to proceed
==============

Two features are used from Docker to Gissmo:

  * volume for data to be persistent on your system
  * link between multiple containers to manage a postgreSQL instance

In fact Gissmo container will be linked to a postgreSQL container that have data on your local system.
For more information about this, check `manage data in containers`_.

.. _manage data in containers: https://docs.docker.com/engine/userguide/containers/dockervolumes/

Let's go installing and configuring!

Database container
==================

First you need to create a volume for database container:

.. code-block:: bash

   docker create -v /dbdata:/var/lib/postgresql/data --name dbdata postgres:9.5
   docker run -d -P --volumes-from dbdata --name gissmo_db postgres:9.5

where:

  * **/dbdata** is the directory where all database data will be saved. Create it.
  * **dbdata** is your volume name
  * **gissmo_db** is your database container name (keep it in mind for next steps)

Database container is up!

.. _gissmo_container:

Gissmo container
================

Steps are:

  * do migration to deploy new schema on database
  * create a superuser
  * launch Gissmo with a link to our database
  * access Gissmo on a web browser

So:

.. code-block:: bash

   docker run -it --rm --link gissmo_db:db fabienengels/gissmo:1.5 python manage.py migrate
   docker run -it --rm --link gissmo_db:db fabienengels/gissmo:1.5 python manage.py createsuperuser
   mkdir ~/upload
   docker run -it --rm -p 8002:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v ~/upload/:/opt/gissmo/uploads fabienengels/gissmo:1.5

where:

  * **~/upload** directory contains uploaded files (from Gissmo)
  * **8002** is your local Gissmo access port, for an example on http://localhost:8002/
  * **gissmo_db** have been launched previously and contains database

**db** is mandatory. Gissmo use it. Gissmo need it as it is! **The link should always be named db**.

Now you're ready to use Gissmo on http://localhost:8002/.

Relaunch container
==================

Each time you need to relaunch the container - for an example after a reboot - you need to:

  * launch database container
  * create gissmo container

Apply this:

.. code-block:: bash

   docker start gissmo_db
   docker run -it --rm -p 8002:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v ~/upload/:/opt/gissmo/uploads fabienengels/gissmo:1.5

Last command is similar to those given in :ref:`gissmo_container` chapter.

Create superuser
================

Gissmo administration needs an administrator called the **superuser**.

**Note**: Database container should be started.

Then:

.. code-block:: bash

   docker run -it --rm --link gissmo_db:db fabienengels/gissmo:1.5 python manage.py createsuperuser

Just answer to what appears on the screen.
