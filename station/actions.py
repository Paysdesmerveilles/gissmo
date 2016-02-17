# -*- coding: utf-8 -*-
from __future__ import unicode_literals


"""
Allowed actions on the given station.

Actions:

  1 : CREER : Create station code
  2 : INSTALLER : Install
  3 : OPERER : Make it as 'operation in progress'
  4 : CONSTATER DEFAUT : Observe failure
  5 : MAINT_PREV_DISTANTE : Perform remote preventive maintenance
  6 : MAINT_CORR_DISTANTE : Perform remote corrective maintenance
  7 : MAINT_PREV_SITE : Perform preventive maintenance locally
  8 : MAINT_CORR_SITE : Perform corrective maintenance locally
  9 : DEMANTELER : Dismantle
  10 : AUTRE : Other
  11 : DEBUTER_TEST : Start test
  12 : TERMINER_TEST : Conclude test
"""
CREER = 1
INSTALLER = 2
OPERER = 3
CONSTATER_DEFAUT = 4
MAINT_PREV_DISTANTE = 5
MAINT_CORR_DISTANTE = 6
MAINT_PREV_SITE = 7
MAINT_CORR_SITE = 8
DEMANTELER = 9
AUTRE = 10
DEBUTER_TEST = 11
TERMINER_TEST = 12
STATION_ACTIONS = (
    (CREER, 'Create station code'),
    (INSTALLER, 'Install station'),
    (DEBUTER_TEST, 'Start test'),
    (TERMINER_TEST, 'Finish test'),
    (OPERER, 'Run'),
    (CONSTATER_DEFAUT, 'Observe failure'),
    (MAINT_PREV_DISTANTE, 'Perform REMOTE PREVentive maintenance'),
    (MAINT_CORR_DISTANTE, 'Perform REMOTE CORrective maintenance'),
    (MAINT_PREV_SITE, 'Perform LOCAL PREVentive maintenance'),
    (MAINT_CORR_SITE, 'Perform LOCAL CORrective maintenance'),
    (DEMANTELER, 'Shut down'),
    (AUTRE, 'Other'),
)
