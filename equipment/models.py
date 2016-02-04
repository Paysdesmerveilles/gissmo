# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class ChangeModelModification(object):
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
    total_number = 0

    def __init__(self, channel):
        self.number = ChangeModelModification.total_number + 1
        self.channel = channel
        self.old_value = None
        self.new_value = None
        self.name = None
        self.state = None

    def get_state(self, compared_values):
        if not self.new_value:
            return 'missing'
        if not self.old_value:
            return 'new'
        both_same = self.old_value == self.new_value
        compatible = self.old_value in compared_values
        if both_same:
            return 'neutral'
        elif not both_same and compatible:
            return 'valid'
        elif not both_same and not compatible:
            return 'conflict'
        # default behaviour
        return 'unknown'
