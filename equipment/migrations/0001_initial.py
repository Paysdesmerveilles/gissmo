# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0026_auto_20160126_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeModelModification',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('state', models.IntegerField(default=1, choices=[(0, 'neutral'), (1, 'unknown'), (2, 'new'), (3, 'valid'), (4, 'conflict'), (5, 'missing')])),
                ('channel', models.ForeignKey(to='gissmo.Channel')),
                ('new_value', models.ForeignKey(null=True, related_name='new_modif', to='gissmo.ParameterValue', blank=True)),
                ('old_value', models.ForeignKey(null=True, related_name='old_modif', to='gissmo.ParameterValue', blank=True)),
            ],
        ),
    ]
