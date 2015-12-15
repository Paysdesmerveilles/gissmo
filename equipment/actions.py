# -*- coding: utf-8 -*-
from __future__ import unicode_literals


"""
Allowed actions on a given Equipment.

Actions:

  1 : ACHETER : Buy
  2 : TESTER : Test
  3 : INSTALLER : Install
  4 : DESINSTALLER : Uninstall
  5 : CONSTATER_DEFAUT : Observe failure
  6 : MAINT_PREV_DISTANTE : Perform remote preventive maintenance
  7 : MAINT_CORR_DISTANTE : Perform remote corrective maintenance
  8 : MAINT_PREV_SITE : Perform preventive maintenance locally
  9 : MAINT_CORR_SITE : Perform corrective maintenance locally
  10 : EXPEDIER : Send
  11 : RECEVOIR : Receive
  12 : METTRE_HORS_USAGE : Put it as out of use
  13 : CONSTATER_DISPARITION : Observe that equipment is lost
  14 : RETROUVER : Find it after being lost
  15 : METTRE_AU_REBUT : Put it as waste
  16 : AUTRE : Other
"""
ACHETER = 1
TESTER = 2
INSTALLER = 3
DESINSTALLER = 4
CONSTATER_DEFAUT = 5
MAINT_PREV_DISTANTE = 6
MAINT_CORR_DISTANTE = 7
MAINT_PREV_SITE = 8
MAINT_CORR_SITE = 9
EXPEDIER = 10
RECEVOIR = 11
METTRE_HORS_USAGE = 12
CONSTATER_DISPARITION = 13
RETROUVER = 14
METTRE_AU_REBUT = 15
AUTRE = 16
EQUIP_ACTIONS = (
    (ACHETER, 'Acheter'),
    (TESTER, 'Tester'),
    (INSTALLER, 'Installer'),
    (DESINSTALLER, 'Désinstaller'),
    (CONSTATER_DEFAUT, 'Constater défaut'),
    (MAINT_PREV_DISTANTE, 'Effectuer maintenance préventive à distance'),
    (MAINT_CORR_DISTANTE, 'Effectuer maintenance corrective à distance'),
    (MAINT_PREV_SITE, 'Effectuer maintenance préventive sur site'),
    (MAINT_CORR_SITE, 'Effectuer maintenance corrective sur site'),
    (EXPEDIER, 'Expédier'),
    (RECEVOIR, 'Recevoir'),
    (METTRE_HORS_USAGE, 'Mettre hors usage'),
    (CONSTATER_DISPARITION, 'Constater disparition'),
    (RETROUVER, 'Retrouver suite à une disparition'),
    (METTRE_AU_REBUT, 'Mettre au rebut'),
    (AUTRE, 'Autre'),
)
