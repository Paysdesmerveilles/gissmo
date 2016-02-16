# -*- coding: utf-8 -*-
from __future__ import unicode_literals


"""
Allowed states for a given Station

States:

  1 : INSTALLATION : Installation in progress
  2 : OPERATION : Operation in progress
  3 : DEFAUT : Failure
  4 : PANNE : Waste
  5 : FERMEE : Closed
  6 : AUTRE : Other
  7 : EN_TEST : Test in progress
"""
INSTALLATION = 1
OPERATION = 2
DEFAUT = 3
PANNE = 4
FERMEE = 5
AUTRE = 6
EN_TEST = 7
STATION_STATES = (
    (INSTALLATION, 'Installing'),
    (EN_TEST, 'Testing'),
    (OPERATION, 'Running'),
    (DEFAUT, 'Broken'),
    (PANNE, 'Failure'),
    (FERMEE, 'Closed'),
    (AUTRE, 'Other'),
)
