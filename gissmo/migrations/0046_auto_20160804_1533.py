# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0045_auto_20160620_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_excluded',
            field=models.BooleanField(default=False, verbose_name="Exclude this project from filters"),
        ),
        migrations.AlterField(
            model_name='project',
            name='sites',
            field=models.ManyToManyField(related_name='projects', blank=True, verbose_name='Site', to='gissmo.StationSite'),
        ),
    ]
