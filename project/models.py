from django.contrib.auth.models import Group
from django.db import models


class Project(Group):
    manager = models.ForeignKey('auth.User',
        related_name='managed_project',
        null=True)
    sites = models.ManyToManyField('place.Site', blank=True)
