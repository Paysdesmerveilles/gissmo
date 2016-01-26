# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0007_auto_20151027_1141'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipdoc',
            name='equip_model',
        ),
        migrations.RemoveField(
            model_name='equipdoc',
            name='equip_supertype',
        ),
        migrations.RemoveField(
            model_name='equipdoc',
            name='equip_type',
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='equip',
            field=models.ForeignKey(verbose_name='equipement', to='gissmo.Equipment'),
        ),
    ]
