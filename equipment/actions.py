# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _


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
    (ACHETER, _('Buy')),
    (TESTER, _('Test')),
    (INSTALLER, _('Install')),
    (DESINSTALLER, _('Uninstall')),
    (CONSTATER_DEFAUT, _('Observe failure')),
    (MAINT_PREV_DISTANTE, _('Perform remote preventive maintenance')),
    (MAINT_CORR_DISTANTE, _('Perform remote corrective maintenance')),
    (MAINT_PREV_SITE, _('Perform preventive maintenance locally')),
    (MAINT_CORR_SITE, _('Perform corrective maintenance locally')),
    (EXPEDIER, _('Send')),
    (RECEVOIR, _('Receive')),
    (METTRE_HORS_USAGE, _('Put is as out of use')),
    (CONSTATER_DISPARITION, _('Observe that equipment is lost')),
    (RETROUVER, _('Find it after being lost')),
    (METTRE_AU_REBUT, _('Put it as waste')),
    (AUTRE, _('Other')),
)
