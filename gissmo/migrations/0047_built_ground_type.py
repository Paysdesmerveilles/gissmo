# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0046_auto_20160701_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='built',
            name='ground_type',
            field=models.ForeignKey(blank=True, verbose_name='EC8 Soil classification', null=True, to='gissmo.GroundType', help_text='See Pitilakis et al. (Bulletin of Earthquake Engineering, 2012) for details'),
        ),
    ]
