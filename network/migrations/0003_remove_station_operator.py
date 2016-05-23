# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_auto_20160510_1314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='station',
            name='operator',
        ),
    ]
