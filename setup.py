#! /usr/bin/env python

from distutils.core import setup

setup(
    name = "bdmateriel",
    version = "1.04",
    author = "Martin Dutil",
    author_email = "mdutil@unistra.fr",
    description = "BD suivi materiel",
    url = "https://teatime.u-strasbg.fr/prj/projects/bdmatos/",
    packages = ['bdmateriel','bdmateriel.templatetags',],
    package_dir = {'bdmateriel': 'src/bdmateriel'},
    package_data = {'bdmateriel': ['templates/*.html','templates/admin/*.html','templates/admin/bdmateriel/*.html','templates/admin/bdmateriel/equipment/*.html','templates/admin/bdmateriel/stationsite/*.html','static/img/*.png','static/js/*.js']},
)
