#! /usr/bin/env python

from distutils.core import setup

setup(
    name = "gissmo",
    version = "1.31",
    author = "Martin Dutil",
    author_email = "mdutil@unistra.fr",
    description = "BD suivi materiel",
    url = "https://teatime.u-strasbg.fr/prj/projects/bdmatos/",
    packages = ['gissmo','gissmo.templatetags',],
    package_dir = {'gissmo': 'src/gissmo'},
    package_data = {'gissmo': ['templates/*.html','templates/*.xml','templates/admin/*.html','templates/admin/gissmo/*.html','templates/admin/gissmo/channel/*.html','templates/admin/gissmo/equipment/*.html','templates/admin/gissmo/network/*.html','templates/admin/gissmo/stationsite/*.html','static/img/*.png','static/js/*.js']},
)
