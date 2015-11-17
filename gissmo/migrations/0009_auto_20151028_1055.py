# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0008_auto_20151028_1034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipmodeldoc',
            name='equip_supertype',
        ),
        migrations.RemoveField(
            model_name='equipmodeldoc',
            name='equip_type',
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='equip_model',
            field=models.ForeignKey(verbose_name="modele d'equipement", to='gissmo.EquipModel'),
        ),
    ]
