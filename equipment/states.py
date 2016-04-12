# -*- coding: utf-8 -*-
from __future__ import unicode_literals


"""
Allowed states on a given Equipment.

Statuses:

  1 : OPERATION : Operation in progress
  2 : A_TESTER : To be tested
  3 : DISPONIBLE : Available
  4 : DEFAUT : Failure
  5 : PANNE : Breakdown
  6 : EN_TRANSIT : Transit in progress
  7 : HORS_USAGE : Out of use
  8 : DISPARU : Lost
  9 : AU_REBUT : Waste
  10 : AUTRE : Other
"""
OPERATION = 1
A_TESTER = 2
DISPONIBLE = 3
DEFAUT = 4
PANNE = 5
EN_TRANSIT = 6
HORS_USAGE = 7
DISPARU = 8
AU_REBUT = 9
AUTRE = 10
EQUIP_STATES = (
    (OPERATION, 'Running'),
    (A_TESTER, 'To be tested'),
    (DISPONIBLE, 'Available'),
    (DEFAUT, 'Ongoing issue'),
    (PANNE, 'Kaputt'),
    (EN_TRANSIT, 'Transit in progress'),
    (HORS_USAGE, 'Out of use'),
    (DISPARU, 'Lost'),
    (AU_REBUT, 'Waste'),
    (AUTRE, 'Other'),
)
