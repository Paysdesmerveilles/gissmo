# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-10 13:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='xml_alternate_code',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='xml_historical_code',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='xml_restricted_status',
        ),
        migrations.RemoveField(
            model_name='network',
            name='xml_alternate_code',
        ),
        migrations.RemoveField(
            model_name='network',
            name='xml_historical_code',
        ),
        migrations.RemoveField(
            model_name='network',
            name='xml_restricted_status',
        ),
        migrations.RemoveField(
            model_name='station',
            name='xml_alternate_code',
        ),
        migrations.RemoveField(
            model_name='station',
            name='xml_historical_code',
        ),
        migrations.RemoveField(
            model_name='station',
            name='xml_restricted_status',
        ),
    ]