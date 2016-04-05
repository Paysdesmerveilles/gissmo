# Installation with Docker

[Docker](https://www.docker.com/) makes it easy to distribute Gissmo by using what Docker call a **container**.

First [install Docker](https://docs.docker.com/).

## Overview

Gissmo docker container takes advantages of:

  * persistent data with volume
  * links between multiple containers (to manage a postgreSQL instance)

In fact Gissmo container will be linked to a postgreSQL container that have data on your local system.
For more information about this, check [manage data in containers](https://docs.docker.com/engine/tutorials/dockervolumes/).

Let's going to install and configure Gissmo!

## Database container

First you need to create a volume for database container:

```bash
docker create -v /dbdata:/var/lib/postgresql/data --name dbdata postgres:9.5
docker run -d -P --volumes-from dbdata --name gissmo_db postgres:9.5
```

where:

  * **/dbdata**: stored database directory. Create it.
  * **dbdata**: database volume name
  * **gissmo_db**: database container name (keep it in mind for next steps)

Database container running!

## Generate Gissmo image

Get source from [Gissmo Github repository](http://github.com/eost/gissmo/).

Then go in gissmo local directory and:

```bash
docker build -t gissmo:1.6 .
```

This will generate a Gissmo docker image.

## Gissmo container

Steps are:

  * do Django migration to deploy new schema on database
  * create a Django superuser
  * launch Gissmo with right links (to our database)
  * check Gissmo application via a webbrowser

So:

```bash
docker run -it --rm --link gissmo_db:db gissmo:1.6 python3 manage.py migrate
docker run -it --rm --link gissmo_db:db gissmo:1.6 python3 manage.py createsuperuser
mkdir ~/upload
docker run -it --rm -p 8002:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v ~/upload/:/opt/gissmo/uploads gissmo:1.6
```

where:

  * **~/upload** directory contains uploaded files (from Gissmo)
  * **8002** is your local Gissmo access port, for an example on http://localhost:8002/
  * **gissmo_db** is your previously launched database container

**db** is mandatory. Gissmo uses it. Gissmo needs it as it is! **The link should always be named db**.

Now you're ready to use Gissmo on [http://localhost:8002/](http://localhost:8002/).

## Relaunch container

Each time you need to relaunch the container - for an example after a reboot - you need to:

  * launch the database container
  * create a gissmo container linked to the database one

So apply this:

```bash
docker start gissmo_db
docker run -it --rm -p 8002:8000 -e SECRET_KEY="abcdefg" --link gissmo_db:db -v ~/upload/:/opt/gissmo/uploads gissmo:1.6
```

Last command is similar to those given in [Gissmo container chapter](#gissmo-container).

## Create superuser via Docker

Gissmo administration needs an administrator called the **superuser**.

**Note**: Database container should be started.

Then:

```bash
docker run -it --rm --link gissmo_db:db gissmo:1.6 python3 manage.py createsuperuser
```

Just answer to what appears on the screen.
