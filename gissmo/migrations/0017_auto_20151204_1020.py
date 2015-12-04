# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0016_auto_20151203_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='latitude',
            field=models.DecimalField(max_digits=8, decimal_places=6, verbose_name='latitude (°)'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='longitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, verbose_name='longitude (°)'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='latitude',
            field=models.DecimalField(max_digits=8, decimal_places=6, blank=True, verbose_name='latitude (°)', null=True),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='longitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, blank=True, verbose_name='longitude (°)', null=True),
        ),
    ]
