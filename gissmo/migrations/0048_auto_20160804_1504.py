# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0047_built_ground_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groundtype',
            options={'verbose_name': 'Soil classification'},
        ),
        migrations.AlterField(
            model_name='built',
            name='ground_type',
            field=models.ForeignKey(to='gissmo.GroundType', blank=True, null=True, help_text='Following EC8 soil classification. See Pitilakis et al. (Bulletin of Earthquake Engineering, 2012) for details', verbose_name='Soil classification'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='ground_type',
            field=models.ForeignKey(to='gissmo.GroundType', blank=True, null=True, help_text='Following EC8 soil classification. See Pitilakis et al. (Bulletin of Earthquake Engineering, 2012) for details', verbose_name='Soil classification'),
        ),
    ]
