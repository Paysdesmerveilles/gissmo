# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def delete_dtinsu_useless_organism(apps, schema_editor):
    """
    As DTINSU is not used, and all users go to "DT INSU" instead, we don't
    need DTINSU as Group.
    """
    Organism = apps.get_model('gissmo', 'Organism')
    Organism.objects.filter(name='DTINSU').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0038_gissmogroup_tweaking'),
    ]

    operations = [
        migrations.RunPython(delete_dtinsu_useless_organism),
    ]
