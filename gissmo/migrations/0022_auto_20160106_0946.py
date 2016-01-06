# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import gissmo.models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0021_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(verbose_name='IP Address')),
                ('netmask', models.GenericIPAddressField(verbose_name='Netmask')),
                ('equipment', models.ForeignKey(to='gissmo.Equipment')),
            ],
        ),
        migrations.RemoveField(
            model_name='service',
            name='ip',
        ),
        migrations.RemoveField(
            model_name='service',
            name='login',
        ),
        migrations.RemoveField(
            model_name='service',
            name='password',
        ),
        migrations.AddField(
            model_name='equipmodel',
            name='is_network_model',
            field=models.BooleanField(verbose_name='Could contains network configuration?', default=False),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='document_equip',
            field=models.FileField(blank=True, upload_to=gissmo.models.equipdoc_file_name, verbose_name='document', storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/upload')),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='document_equip_model',
            field=models.FileField(blank=True, upload_to=gissmo.models.equipmodeldoc_file_name, verbose_name='document', storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/upload')),
        ),
        migrations.AlterField(
            model_name='service',
            name='protocol',
            field=models.IntegerField(verbose_name='Protocol', choices=[(0, 'SSH protocol'), (1, 'Seed link protocol'), (2, 'HTTP'), (3, 'HTTPS'), (4, 'SNMP'), (5, 'ICMP')]),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='document_station',
            field=models.FileField(blank=True, upload_to=gissmo.models.stationdoc_file_name, verbose_name='document', storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/upload')),
        ),
    ]
