.. GISSMO documentation master file, created by
   sphinx-quickstart on Tue Apr  5 08:09:25 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to GISSMO's documentation!
==================================

Description
-----------

GISSMO stands for *Gestion Informatisée pour le Suivi des Sites et du Matériel sismOlogique* (in french) which means that it's an electronic management system for sismologic stuff and places.

You should be able to:

  * manage stuff (model, type, serial number, etc.)
  * manage places (site, builts, etc.)
  * manage users (project, permission, etc.)
  * manage channels on sites (network, configuration)
  * manage interventions on each site
  * link documents on each place, intervention, etc.
  * display sites on a map

GISSMO is delivered as a web application.

Installation
------------

There is 2 ways to install GISSMO:

  * [recommended] :doc:`using Docker <installation_docker>`
  * :doc:`using Python virtual environment <installation_venv>`

If you need more information, please have a look to :doc:`Developer's guide <development>`.

For GISSMO first use, see :ref:`getting_started`.

.. _getting_started:

Getting started
---------------

First time you use GISSMO you need to :doc:`create some data and understand Gissmo interface<getting_started>`.

Contents
--------

This documentation is composed of:

.. toctree::
   :maxdepth: 2

   installation_docker
   installation_venv
   getting_started
   development

Source
------

`GISSMO is available on Github`_.

.. _GISSMO is available on Github: http://github.com/eost/gissmo/

License
-------

.. todo::

   WHICH LICENSE SHOULD WE ADD? For now, CeCiLL seems to be the best choice

Community
---------

Join us on IRC: `#gissmo on freenode`_.

.. _#gissmo on freenode: http://webchat.freenode.net?channels=%23gissmo

Contributors
------------

  * `Olivier DOSSMANN`_
  * `Fabien ENGELS`_
  * `Martin DUTIL`_

.. _Olivier DOSSMANN: http://github.com/blankoworld
.. _Fabien ENGELS: http://github.com/fabienengels
.. _Martin DUTIL: http://github.com/mdutil

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

