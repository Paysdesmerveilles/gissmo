# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametervalue',
            name='default_value',
            field=models.BooleanField(
                default=None,
                verbose_name='valeur par defaut'),
        ),
    ]
