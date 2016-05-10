# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0043_rename_inconnu_to_unknown'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='last_state',
            field=models.IntegerField(choices=[(1, 'Running'), (2, 'To be tested'), (3, 'Available'), (4, 'Ongoing issue'), (5, 'Out of order'), (6, 'In transit'), (7, 'Unusable'), (8, 'Lost'), (9, 'Dismantled'), (10, 'Other')], blank=True, null=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip_action',
            field=models.IntegerField(choices=[(1, 'Buy'), (2, 'Test'), (3, 'Install'), (4, 'Uninstall'), (5, 'Report problem'), (6, 'Perform remote preventive maintenance'), (7, 'Perform remote corrective maintenance'), (8, 'Perform preventive maintenance locally'), (9, 'Perform corrective maintenance locally'), (10, 'Send'), (11, 'Receive'), (12, 'Report unusable'), (13, 'Report lost equipment'), (14, 'Recover lost equipment'), (15, 'Dump definitively'), (16, 'Other')], verbose_name='Action'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip_state',
            field=models.IntegerField(choices=[(1, 'Running'), (2, 'To be tested'), (3, 'Available'), (4, 'Ongoing issue'), (5, 'Out of order'), (6, 'In transit'), (7, 'Unusable'), (8, 'Lost'), (9, 'Dismantled'), (10, 'Other')], verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='station_action',
            field=models.IntegerField(choices=[(1, 'Create station code'), (2, 'Prepare station'), (11, 'Start test'), (12, 'Finish test'), (3, 'Operate station'), (4, 'Report problem'), (5, 'Perform REMOTE PREVentive maintenance'), (6, 'Perform REMOTE CORrective maintenance'), (7, 'Perform LOCAL PREVentive maintenance'), (8, 'Perform LOCAL CORrective maintenance'), (9, 'Close station'), (10, 'Other')], verbose_name='Action'),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='station_state',
            field=models.IntegerField(choices=[(1, 'In installation'), (2, 'Running'), (3, 'Major failure'), (4, 'Ongoing issue'), (5, 'Closed'), (6, 'Other'), (7, 'In test')], blank=True, null=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='last_state',
            field=models.IntegerField(choices=[(1, 'In installation'), (2, 'Running'), (3, 'Major failure'), (4, 'Ongoing issue'), (5, 'Closed'), (6, 'Other'), (7, 'In test')], blank=True, null=True, verbose_name='Status'),
        ),
    ]
