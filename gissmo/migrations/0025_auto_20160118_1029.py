# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import gissmo.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0024_auto_20160114_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipaddress',
            name='ip',
            field=models.CharField(verbose_name='IP Address', validators=[gissmo.validators.validate_ipaddress], max_length=255),
        ),
    ]
