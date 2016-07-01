# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0045_auto_20160620_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='protocol',
            field=models.IntegerField(choices=[(0, 'SSH protocol'), (1, 'Seed link protocol'), (2, 'HTTP'), (3, 'HTTPS'), (4, 'SNMP'), (5, 'ICMP'), (6, 'Telnet'), (7, 'FTP')], verbose_name='Protocol'),
        ),
    ]
