# Developer's guide

Welcome to this developer area where you will find how to improve Gissmo.

## Overview

Gissmo gets priority to **[Docker](http://docker.com/)** in order to have a Django instance.


  * [Source repository](https://github.com/eost/gissmo) (using Github)
  * [Bugs and improvements](https://github.com/eost/gissmo/issues) can be found on Github
  * [Flake8 script that checks your code before a commit](https://github.com/eost/gissmo/blob/master/scripts/git_hooks/pre-commit)
  * [Mkdocs](http://mkdocs.org/) as documentation generator. We choose **Markdown** format. [Gissmo documentation](https://gissmo.readthedocs.org) is hosted by [Readthedocs](https://readthedocs.org/).

Tests are done on in a [python virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and automatically launched with [Travis](https://travis-ci.org/), just check [Gissmo Travis page](https://travis-ci.org/eost/gissmo).

## Git commit code convention

In our repository you will find commits with some tag. For an example:

```
[UP] Complete documentation
```

Their meaning:


  * **FIX**: Fix a problem, a bug, etc.
  * **IMP**: New feature or improve the way a code works
  * **ADD**: Add a file, a new thing, etc.
  * **DEL**: Delete something (a file, a feature, etc.)
  * **UP**: Update a file as README file, TODO list, etc.
  * **WIP**: Work In Progress
  * **REF**: Refactorization
  * **OPT**: Optimization

Use them in your commits.

## Howto check code before commiting (with flake8)

We consider that:

  * you have Gissmo source code
  * you created a python virtual environment

In order Git to check code before each commit, use **scripts/git_hooks/pre-commit** script:

```bash
cp scripts/git_hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Then commit (Python virtual environment should be activated). This will check the code and display potential errors.

## Link a virtualenv with a postgreSQL container

If you have a postgreSQL container, and Gissmo in a Python virtualenv, use **POSTGRES_PORT** environment variable with **docker inspect** command to launch Django:

```bash
POSTGRES_PORT=`docker inspect -f '{{ (index (index .NetworkSettings.Ports "5432/tcp") 0).HostPort}}' gissmo_db` python3 manage.py runserver
```

where **gissmo_db** is your database container name and **5432/tcp** is your postgreSQL container hosted port.

## Run tests

To run tests:

  * create a postgreSQL container called **gissmo_db** using Docker
  * enter Gissmo source code with a Python virtualenv in which you install Gissmo python dependencies (using *pip install -r requirements*)

Then launch this command (available in Gissmo source code):

```bash
./scripts/launch-tests.sh app_name
```

where **app_name** is the application name you want to test.

For an example we have:

  * **functional_tests**: to launch some functional tests using Firefox
  * **gissmo**: to launch non-graphical tests

**Tip**: You can also launch a specific test using this syntax:

```bash
./scripts/launch-tests.sh app_name.NamedClass.test_method_name
```

for an example:

```bash
./scripts/launch-tests.sh functional_tests.tests.ProjectTest.test_project_creation
```

## Generate documentation

Enter into a python virtualenv. Then go to Gissmo source code and do:

```bash
pip install -r requirements  # Check dependancies
mkdocs build
```

Documentation is now located in **site** directory.

If you need more, have a look to [Mkdocs](http://mkdocs.org/) official documentation.

## Docker entrypoint commands

As Docker container starts using a specific entrypoint, it delivers multiple possibilities:

  * (default) **production**: start a uWSGI server
  * **test**: start a uWSGI server with DEBUG=True to display errors
  * **development**: start the Django python webserver
  * **manage [argument ...]**: launch ```python3 manage.py [argument ...]``` into the container
  * **migrate**: make a database migration using ```python3 manage.py migrate``` command. This takes NO more arguments

**production** mode needs a SECRET_KEY environment variable to work well.

To launch the Docker container using one of these ways, just do:

```bash
docker run -it --rm -P --link gissmo_db:db -v /srv/upload:/data gissmo:1.7 development
```

where:

  * **gissmo_db** is your database container name
  * **db** should not be changed
  * **/srv/upload** is your local upload storage directory

You can also launch commands into the Docker container with the **development** version:

```bash
docker run -it --rm -P --link gissmo_db:db -v /srv/upload:/data gissmo:1.7 development python3 manage.py migrate
```

Have fun with Docker containers!

## Docker container management tool

[Gissmo Launch Script](https://bitbucket.org/blankoworld/eost_gissmo_tools) is a tool that helps developer to fetch Gissmo source code, initializes postgreSQL Docker container, start a Gissmo Docker container with a link to the previous one and mount volumes to share current development directory with containers.

Create a configuration file regarding the [config.example file](https://bitbucket.org/blankoworld/eost_gissmo_tools/src/e01e324b2b52ee2408ef198a86ae74c4be2acac4/config.example?fileviewer=file-view-default) and place it here: **~/.config/gissmo**.

Then to start a Gissmo project, do:

```bash
./launch.sh init
./launch.sh create
./launch.sh migrate
./launch.sh dev
```

After that, each time you want to launch Gissmo, just do:

```bash
./launch.sh dev
```

It will do the trick!

**This tool is done by a Gissmo contributor. We're not responsible for any kind of damages and problems that occurs using this tool.**

## Export database schema as a diagram

Django permits developer to export all models from a given application to a dot file.

You need **django-extension** module for this tip to work.

Then:

    python3 manage.py graph_models gissmo > schema.dot
    dot -Tpng schema.dot > schema.png

## Export database structure from postgreSQL to a CSV file

With psql on host (that connect you to Docker container), you can use this command:

    COPY (select table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' order by table_name) TO '/var/lib/postgresql/data/nawak.csv' DELIMITER ',' CSV HEADER; 

then fetch your file in database storage directory (for an example /dbdata).
