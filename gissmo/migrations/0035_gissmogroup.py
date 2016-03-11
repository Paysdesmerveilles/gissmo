# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
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
                ('group', models.OneToOneField(to='auth.Group', primary_key=True, serialize=False)),
                ('manager', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('sites', models.ManyToManyField(verbose_name='Site', blank=True, to='gissmo.StationSite')),
            ],
            bases=('auth.group',),
        ),
    ]
