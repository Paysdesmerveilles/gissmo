# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import datetime
import equipment.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('equipment', '0001_firstone'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='last_edition',
            field=models.DateTimeField(verbose_name='Last edition', default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='equipment',
            name='last_user',
            field=models.ForeignKey(related_name='last_user', verbose_name='Modified by', default=equipment.models.Equipment.user_default, to=settings.AUTH_USER_MODEL),
        ),
    ]
