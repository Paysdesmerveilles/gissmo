from __future__ import unicode_literals

from django.utils import timezone

from decimal import Decimal
import json
from datetime import datetime, time


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def timezone_aware(naive_datetime):
    current_timezone = timezone.get_current_timezone()
    return naive_datetime.replace(tzinfo=current_timezone)


def make_date_aware(field):
    """
    Adapt given field to an aware date.
    If datetime, all is OK, just check timezone.
    If date, time is missing. Add it.
    If string, time is missing. Add it.
    """
    if not isinstance(field, datetime):
        if isinstance(field, str):
            field = datetime.strptime(field, '%Y-%m-%d')
        t = time(0, 0, 0)
        field = datetime.combine(field, t)
        return timezone.make_aware(field)
    return field
