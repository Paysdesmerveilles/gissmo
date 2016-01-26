# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0014_equipment_last_station'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='equipaction',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='stationaction',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='stationstate',
            options={'managed': False},
        ),
        migrations.DeleteModel('EquipState'),
        migrations.DeleteModel('EquipAction'),
        migrations.DeleteModel('StationAction'),
        migrations.DeleteModel('StationState'),
    ]
