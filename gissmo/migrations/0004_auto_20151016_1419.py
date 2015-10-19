# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import gissmo.models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0003_auto_20151012_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipdoc',
            name='document_equip',
            field=models.FileField(
                upload_to=gissmo.models.equipdoc_file_name,
                storage=django.core.files.storage.FileSystemStorage(
                    location=b'/opt/gissmo/upload'),
                verbose_name='document',
                blank=True),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='document_equip_model',
            field=models.FileField(
                upload_to=gissmo.models.equipmodeldoc_file_name,
                storage=django.core.files.storage.FileSystemStorage(
                    location=b'/opt/gissmo/upload'),
                verbose_name='document',
                blank=True),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='document_station',
            field=models.FileField(
                upload_to=gissmo.models.stationdoc_file_name,
                storage=django.core.files.storage.FileSystemStorage(
                    location=b'/opt/gissmo/upload'),
                verbose_name='document',
                blank=True),
        ),
    ]
