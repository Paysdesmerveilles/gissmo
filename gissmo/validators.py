from __future__ import unicode_literals


from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import ugettext_lazy as _

import re


def validate_ipaddress(value):
    is_host = False
    is_ipv4 = False
    host_match = re.search(URLValidator.host_re, value)
    if host_match:
        is_host = True
    ipv4_match = re.search(URLValidator.ipv4_re, value)
    if ipv4_match:
        is_ipv4 = True
    if not is_host and not is_ipv4:
        raise ValidationError(
            _('%s is neither a host nor an IPv4 address') % value)


def validate_equip_model(value):
    from gissmo.models import ForbiddenEquipmentModel
    equipment = ForbiddenEquipmentModel.objects.filter(original=value).first()
    if equipment:
        raise ValidationError(
            _('Forbidden! Please use %(recommended)s instead'),
            params={'recommended': equipment.recommended}
        )
