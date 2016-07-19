# Gissmo

Gissmo aims to be a web management system for tagged equipments located on some places, especially in seismological stations. It gives information about how to access data on each station via a RESTful API.

Gissmo is used by seismological french network ([RESIF](http://www.resif.fr/)).

[![Build Status](https://travis-ci.org/eost/gissmo.svg)](https://travis-ci.org/eost/gissmo)
[![Documentation](https://readthedocs.org/projects/gissmo/badge/?version=stable)](http://gissmo.readthedocs.io/en/stable/)
[![Python 3.4](https://img.shields.io/badge/python-3.4-green.svg)](http://python.org/)
[![Django 1.8.13](https://img.shields.io/badge/django-1.8.13-green.svg)](http://djangoproject.com/)
[![postgreSQL 9.5](https://img.shields.io/badge/postgreSQL-9.5-green.svg)](http://postgresql.org/)
[![CeCILL 2.1](https://img.shields.io/badge/License-CeCILL-blue.svg)](http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html)

# Overview

Gissmo is based on [Django](http://djangoproject.com/) to display a web interface and a RESTful API.

It manages users, projects and assembles equipments by model and type.

With Gissmo you can:

  * add IP addresses and services on each equipment
  * create a data acquisition chain by using channel concept
  * keep an history of intervention that occurs on equipments and stations
  * generate a [StationXML file](http://www.fdsn.org/xml/station/) for each station
  * display stations map
  * visualize your station on Google Map
  * create default equipment configuration and use it as default for each channel
  * attach documents on station, intervention, equipments and models
  * create 3 channels in a one-step wizard for a given station
  * and more…

Gissmo is designed for seismology. But it is useful in case you manage location with a sheet of paper or a spreadsheet.

# Documentation

[Gissmo documentation on Readthedocs](http://gissmo.readthedocs.io).

# License

Gissmo is licensed under the [CeCILL 2.1](./LICENSE) license.

# Contributors

* [Olivier Dossmann](https://github.com/blankoworld)
* [Fabien Engels](https://github.com/fabienengels)
* [Martin Dutil](https://github.com/mdutil)
