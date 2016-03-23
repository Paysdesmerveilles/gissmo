# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0039_delete_dtinsu_duplicate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationsite',
            name='station_parent',
            field=models.ForeignKey(null=True, to='gissmo.StationSite', verbose_name='Referent', blank=True),
        ),
    ]
