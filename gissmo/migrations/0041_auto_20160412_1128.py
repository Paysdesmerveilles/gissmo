# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0040_linked_site_field_renamed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='last_state',
            field=models.IntegerField(verbose_name='Status', blank=True, choices=[(1, 'Running'), (2, 'To be tested'), (3, 'Available'), (4, 'Ongoing issue'), (5, 'Kaputt'), (6, 'Transit in progress'), (7, 'Out of use'), (8, 'Lost'), (9, 'Waste'), (10, 'Other')], null=True),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip_action',
            field=models.IntegerField(verbose_name='Action', choices=[(1, 'Buy'), (2, 'Test'), (3, 'Install'), (4, 'Uninstall'), (5, 'Report failure'), (6, 'Perform remote preventive maintenance'), (7, 'Perform remote corrective maintenance'), (8, 'Perform preventive maintenance locally'), (9, 'Perform corrective maintenance locally'), (10, 'Send'), (11, 'Receive'), (12, 'Put is as out of use'), (13, 'Observe that equipment is lost'), (14, 'Find it after being lost'), (15, 'Put it as waste'), (16, 'Other')]),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip_state',
            field=models.IntegerField(verbose_name='Status', choices=[(1, 'Running'), (2, 'To be tested'), (3, 'Available'), (4, 'Ongoing issue'), (5, 'Kaputt'), (6, 'Transit in progress'), (7, 'Out of use'), (8, 'Lost'), (9, 'Waste'), (10, 'Other')]),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='station_action',
            field=models.IntegerField(verbose_name='Action', choices=[(1, 'Create station code'), (2, 'Install station'), (11, 'Start test'), (12, 'Finish test'), (3, 'Operate station'), (4, 'Report failure'), (5, 'Perform REMOTE PREVentive maintenance'), (6, 'Perform REMOTE CORrective maintenance'), (7, 'Perform LOCAL PREVentive maintenance'), (8, 'Perform LOCAL CORrective maintenance'), (9, 'Shut down'), (10, 'Other')]),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='station_state',
            field=models.IntegerField(verbose_name='Status', blank=True, choices=[(1, 'In installation'), (7, 'In test'), (2, 'Running'), (3, 'Kaputt'), (4, 'Ongoing issue'), (5, 'Closed'), (6, 'Other')], null=True),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='last_state',
            field=models.IntegerField(verbose_name='Status', blank=True, choices=[(1, 'In installation'), (7, 'In test'), (2, 'Running'), (3, 'Kaputt'), (4, 'Ongoing issue'), (5, 'Closed'), (6, 'Other')], null=True),
        ),
    ]
