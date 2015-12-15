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
    (CREER, 'Créer code station'),
    (INSTALLER, 'Installer station'),
    (DEBUTER_TEST, 'Débuter test'),
    (TERMINER_TEST, 'Terminer test'),
    (OPERER, 'Mettre en opération'),
    (CONSTATER_DEFAUT, 'Constater défaillance'),
    (MAINT_PREV_DISTANTE, 'Effectuer maintenance préventive à distance'),
    (MAINT_CORR_DISTANTE, 'Effectuer maintenance corrective à distance'),
    (MAINT_PREV_SITE, 'Effectuer maintenance préventive sur site'),
    (MAINT_CORR_SITE, 'Effectuer maintenance corrective sur site'),
    (DEMANTELER, 'Démanteler'),
    (AUTRE, 'Autre'),
)
