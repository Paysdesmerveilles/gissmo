from __future__ import unicode_literals
import pytz
from django.conf import settings
from django.utils.datetime_safe import new_datetime


def format_date(date_obj):
    # Fix datetime < 1900 ...
    # https://github.com/django/django/blob/master/django/utils/datetime_safe.py
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    date_obj = new_datetime(date_obj)
    date_obj.astimezone(local_timezone)
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")
