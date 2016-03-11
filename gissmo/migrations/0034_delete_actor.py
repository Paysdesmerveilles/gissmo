# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0033_intervactor_split'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actor',
            name='actor_parent',
        ),
        migrations.RemoveField(
            model_name='intervactor',
            name='actor',
        ),
        migrations.RemoveField(
            model_name='intervactor',
            name='intervention',
        ),
        migrations.DeleteModel(
            name='Actor',
        ),
        migrations.DeleteModel(
            name='IntervActor',
        ),
    ]
