# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0009_auto_20151028_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='purchase_date',
            field=models.DateField(null=True, blank=True, verbose_name='Date achat'),
        ),
    ]
