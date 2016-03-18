# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
        ('gissmo', '0034_delete_actor'),
    ]

    operations = [
        migrations.CreateModel(
            name='GissmoGroup',
            fields=[
                ('group_ptr', models.OneToOneField(to='auth.Group', primary_key=True, serialize=False, auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True)),
                ('manager', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('sites', models.ManyToManyField(verbose_name='Site', blank=True, to='gissmo.StationSite')),
            ],
            bases=('auth.group',),
        ),
    ]
