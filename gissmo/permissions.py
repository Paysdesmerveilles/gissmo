# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions

from django.conf import settings
from django.http.request import validate_host


class WhitelistPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_permission(self, request, view):
        ip_addr = request.META['REMOTE_ADDR']
        return validate_host(ip_addr, settings.API_ALLOWED_HOSTS)
