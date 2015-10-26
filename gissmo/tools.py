from __future__ import unicode_literals
from django.utils import timezone
from decimal import Decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def timezone_aware(naive_datetime):
    current_timezone = timezone.get_current_timezone()
    return naive_datetime.replace(tzinfo=current_timezone)
