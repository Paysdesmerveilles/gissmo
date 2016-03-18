# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def delete_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for group in Group.objects.all():
        if group.name != 'Resif':
            group.delete()


def migrate_projects_to_group(apps, schema_editor):
    Project = apps.get_model('gissmo', 'Project')
    Group = apps.get_model('gissmo', 'GissmoGroup')
    for project in Project.objects.all():
        # Create first project as Group
        g = Group.objects.create(name=project.project_name)
        # Add manager
        g.manager = project.manager
        # Add users
        for puser in project.projectuser_set.all():
            g.user_set.add(puser.user)
        g.save()
        # Link sites to Group
        for site in project.station.all():
            g.sites.add(site)
        g.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0035_gissmogroup'),
    ]

    operations = [
        migrations.RunPython(delete_groups),
        migrations.RunPython(migrate_projects_to_group),
    ]
