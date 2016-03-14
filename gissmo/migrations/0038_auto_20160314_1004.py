# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_resif_group_to_gissmogroup(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    GissmoGroup = apps.get_model('gissmo', 'GissmoGroup')
    resif = Group.objects.filter(name='Resif').first()
    GissmoGroup.objects.create(name=resif.name, group=resif)


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0037_auto_20160311_1546'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gissmogroup',
            options={'verbose_name': 'Gissmo specific'},
        ),
        migrations.RunPython(migrate_resif_group_to_gissmogroup),
    ]
