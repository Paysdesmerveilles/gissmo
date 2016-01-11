# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions

from django.conf import settings
from django.http.request import validate_host


class WhitelistPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    If '*' is in API_ALLOWED_HOSTS, we accept all IPs.
    """

    def has_permission(self, request, view):
        if '*' in settings.API_ALLOWED_HOSTS:
            return True
        ip_addr = request.META['REMOTE_ADDR']
        return validate_host(ip_addr, settings.API_ALLOWED_HOSTS)
