# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0010_equipment_purchase_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='stationsite',
            name='creation_date',
            field=models.DateField(null=True, verbose_name='Date création', blank=True),
        ),
    ]
