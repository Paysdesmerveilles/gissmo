# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import gissmo.models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0019_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipdoc',
            name='document_equip',
            field=models.FileField(verbose_name='document', storage=django.core.files.storage.FileSystemStorage(location='/opt/gissmo/upload'), upload_to=gissmo.models.equipdoc_file_name, blank=True),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='document_equip_model',
            field=models.FileField(verbose_name='document', storage=django.core.files.storage.FileSystemStorage(location='/opt/gissmo/upload'), upload_to=gissmo.models.equipmodeldoc_file_name, blank=True),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='document_station',
            field=models.FileField(verbose_name='document', storage=django.core.files.storage.FileSystemStorage(location='/opt/gissmo/upload'), upload_to=gissmo.models.stationdoc_file_name, blank=True),
        ),
    ]
