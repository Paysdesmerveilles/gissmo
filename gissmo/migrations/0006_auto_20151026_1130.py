# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0005_auto_20151019_1314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipmodel',
            name='equip_supertype',
        ),
        migrations.AlterField(
            model_name='equipmodel',
            name='equip_type',
            field=models.ForeignKey(to='gissmo.EquipType', verbose_name="type d'equipement"),
        ),
    ]
