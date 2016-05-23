# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('place', '0002_auto_20160502_1325'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, to='auth.Group', parent_link=True, primary_key=True, serialize=False)),
                ('manager', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='managed_project')),
                ('places', models.ManyToManyField(to='place.Place', blank=True)),
            ],
            bases=('auth.group',),
        ),
    ]
