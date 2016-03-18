# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0031_auto_20160310_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='owner',
            field=models.ForeignKey(verbose_name='Owner', to='gissmo.Organism')),
        migrations.AlterField(
            model_name='stationsite',
            name='operator',
            field=models.ForeignKey(verbose_name='Operator', to='gissmo.Organism')),
    ]
