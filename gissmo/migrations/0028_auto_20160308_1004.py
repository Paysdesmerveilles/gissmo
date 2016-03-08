# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0027_auto_20160216_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntervDoc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('_file', models.FileField(upload_to='intervention/%Y/%m/%d/', storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/project/gissmo/upload'), blank=True, verbose_name='File')),
                ('description', models.CharField(max_length=255)),
                ('intervention', models.ForeignKey(to='gissmo.Intervention')),
            ],
        ),
        migrations.AlterField(
            model_name='chain',
            name='order',
            field=models.IntegerField(choices=[(1, 'Sensor'), (2, 'PreAmplifier'), (3, 'DataLogger'), (4, 'Equipment'), (5, 'Other_1'), (6, 'Other_2'), (7, 'Other_3'), (8, 'Other_4'), (9, 'Other_5')], verbose_name='Type'),
        ),
    ]
