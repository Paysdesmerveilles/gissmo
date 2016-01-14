# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import gissmo.models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0023_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipdoc',
            name='document_equip',
            field=models.FileField(upload_to=gissmo.models.equipdoc_file_name, verbose_name='document', blank=True, storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/project/gissmo/upload')),
        ),
        migrations.AlterField(
            model_name='equipmodel',
            name='manufacturer',
            field=models.CharField(max_length=50, default='Unknown', verbose_name='manufacturer'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='document_equip_model',
            field=models.FileField(upload_to=gissmo.models.equipmodeldoc_file_name, verbose_name='document', blank=True, storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/project/gissmo/upload')),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='document_station',
            field=models.FileField(upload_to=gissmo.models.stationdoc_file_name, verbose_name='document', blank=True, storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/project/gissmo/upload')),
        ),
    ]
