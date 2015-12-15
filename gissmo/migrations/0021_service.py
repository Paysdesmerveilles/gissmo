# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0020_auto_20151215_1632'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol', models.IntegerField(verbose_name='Protocol', choices=[(0, 'SSH protocol'), (1, 'Seed link protocol')])),
                ('ip', models.GenericIPAddressField(verbose_name='IP Address')),
                ('port', models.PositiveIntegerField(verbose_name='Port')),
                ('login', models.CharField(verbose_name='Login', max_length=256)),
                ('password', models.CharField(verbose_name='Password', max_length=256)),
                ('description', models.CharField(blank=True, max_length=256, verbose_name='Description', null=True)),
                ('equipment', models.ForeignKey(to='gissmo.Equipment')),
            ],
        ),
    ]
