# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0011_stationsite_creation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='equipments',
            field=models.ManyToManyField(to='gissmo.Equipment', verbose_name='Equipments', through='gissmo.Chain'),
        ),
    ]
