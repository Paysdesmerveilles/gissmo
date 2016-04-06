Installation using Docker
*************************

`Docker`_ make it easy to deliver applications in a container. Which have been used with GISSMO to distribute it easily.

So You need to `install Docker`_ (link for Linux) first.

.. _Docker: https://www.docker.com/
.. _install Docker: https://docs.docker.com/linux/step_one/

How this will work
==================

We will first use a database container (i.e postgreSQL) on a given directory to keep data from GISSMO. If you want more, see `manage data in containers`_ on Docker website.

.. _manage data in containers: https://docs.docker.com/engine/userguide/containers/dockervolumes/

Then we will create a GISSMO container with a link with the previous one in order to have access to data.

Database container
==================

First you need to create a volume for database container:

.. code-block:: bash

   docker create -v /dbdata:/var/lib/postgresql/data --name dbdata postgres:9.5
   docker run -d -P --volumes-from dbdata --name gissmo_db postgres:9.5

where:

  * **/dbdata** is the directory where all data will be saved
  * **dbdata** is your volume name
  * **gissmo_db** is your database container name

Your database container is up!

.. _gissmo_container:

Gissmo container
================

We will apply steps in this order:

  * apply migration on database to create new schema
  * create a superuser
  * launch a Gissmo container using our database one
  * check it works using a web browser

So:

.. code-block:: bash

   docker run -it --rm --link gissmo_db:db fabienengels/gissmo:1.5 python manage.py migrate
   docker run -it --rm --link gissmo_db:db fabienengels/gissmo:1.5 python manage.py createsuperuser
   mkdir ~/upload
   docker run -it --rm -p 8002:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v ~/upload/:/opt/gissmo/uploads fabienengels/gissmo:1.5

where:

  * **~/upload** is the directory where you will have uploaded files
  * **8002** is the port from where you will access Gissmo, for an example on http://localhost:8002/
  * **gissmo_db** is our previous database container name (should be launched)

Note that **:db** is mandatory as Gissmo use it.

You're ready to use Gissmo: http://localhost:8002/.

Relaunch container
==================

Next time you want to relaunch your container - for an example after a reboot - you need to:

  * launch database container
  * create gissmo container

To do it:

.. code-block:: bash

   docker start gissmo_db
   docker run -it --rm -p 8002:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v ~/upload/:/opt/gissmo/uploads fabienengels/gissmo:1.5

Last command is similar to those given in :ref:`gissmo_container` chapter.
