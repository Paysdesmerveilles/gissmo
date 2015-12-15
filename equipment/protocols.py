# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _


"""
Allowed protocols on a given Equipment.

Protocols:

  0: SSH
  1: seedlink
"""

SSH = 0
SEED_LINK = 1

PROTOCOL_CHOICES = (
    (SSH, _('SSH protocol')),
    (SEED_LINK, _('Seed link protocol')),
)
