# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0036_migrate_project_to_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='manager',
        ),
        migrations.RemoveField(
            model_name='project',
            name='station',
        ),
        migrations.RemoveField(
            model_name='projectuser',
            name='project',
        ),
        migrations.RemoveField(
            model_name='projectuser',
            name='user',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
        migrations.DeleteModel(
            name='ProjectUser',
        ),
    ]
