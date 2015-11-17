# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0006_auto_20151026_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='equip_model',
            field=models.ForeignKey(verbose_name="modele d'equipement", to='gissmo.EquipModel'),
        ),
        migrations.AlterUniqueTogether(
            name='equipment',
            unique_together=set([('equip_model', 'serial_number')]),
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='equip_supertype',
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='equip_type',
        ),
    ]
