# -*- coding: utf-8 -*-
from __future__ import unicode_literals


"""
Allowed protocols on a given Equipment.

Protocols:

  0: SSH
  1: seedlink
"""

SSH = 0
SEED_LINK = 1
HTTP = 2
HTTPS = 3
SNMP = 4
ICMP = 5

PROTOCOL_CHOICES = (
    (SSH, 'SSH protocol'),
    (SEED_LINK, 'Seed link protocol'),
    (HTTP, 'HTTP'),
    (HTTPS, 'HTTPS'),
    (SNMP, 'SNMP'),
    (ICMP, 'ICMP'),
)
