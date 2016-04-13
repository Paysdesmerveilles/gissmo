# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0042_auto_20160412_1412'),
    ]

    operations = [
        migrations.RunSQL("UPDATE gissmo_organism set name = 'Unknown' WHERE name = 'Inconnu';"),
    ]
