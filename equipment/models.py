# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class ChangeModelModification(models.Model):
    """
    This class represents a modification from a specific parameter value
    to a new one.
    States:
      - neutral: both new and old value are equal
      - valid: new value is compatible with old value (regarding new values
      list)
      - conflict: old value is not compatible with new values list
      - new: no old value. Just a new value
      - missing: no new value
    """
    NEUTRAL = 0
    UNKNOWN = 1
    NEW = 2
    VALID = 3
    CONFLICT = 4
    MISSING = 5

    STATE_CHOICES = (
        (NEUTRAL, _('neutral')),
        (UNKNOWN, _('unknown')),
        (NEW, _('new')),
        (VALID, _('valid')),
        (CONFLICT, _('conflict')),
        (MISSING, _('missing')),
    )

    channel = models.ForeignKey('gissmo.Channel')
    name = models.CharField(max_length=255)
    old_value = models.ForeignKey(
        'gissmo.ParameterValue',
        null=True,
        blank=True,
        related_name='old_modif')
    new_value = models.ForeignKey(
        'gissmo.ParameterValue',
        null=True,
        blank=True,
        related_name='new_modif')
    state = models.IntegerField(
        choices=STATE_CHOICES,
        default=UNKNOWN)

    def get_state(self):
        if not self.new_value:
            return self.MISSING
        if not self.old_value:
            return self.NEW
        both_same = self.old_value.value == self.new_value.value
        values = self.new_value.parameter.parametervalue_set.all()
        compared_values = []
        for value in values:
            compared_values.append(value.value)
        compatible = self.old_value.value in compared_values
        if both_same:
            return self.NEUTRAL
        elif not both_same and compatible:
            return self.VALID
        elif not both_same and not compatible:
            return self.CONFLICT
        # default behaviour
        return self.UNKNOWN

    def _get_values(self):
        "Return all possible values linked to new_value parameter."
        if self.new_value:
            return self.new_value.parameter.parametervalue_set.all()
        return []

    _get_values.short_description = _('values')

    values = property(_get_values)

    def __str__(self):
        return "%s" % self.name or ''
