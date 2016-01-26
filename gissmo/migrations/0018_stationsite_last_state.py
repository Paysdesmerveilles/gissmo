# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_last_station_state(apps, schema_editor):
    """
    All stations ' states are in IntervStation.
    We now have a specific field in Station to know the last one:
    last_state.
    So we need to copy the last known value from IntervStation to Station.
    """
    StationSite = apps.get_model('gissmo', 'StationSite')
    IntervStation = apps.get_model('gissmo', 'IntervStation')
    stations = StationSite.objects.all()
    for s in stations:
        intervention = IntervStation.objects.filter(
            intervention__station_id=s.id,
            station_state__isnull=False).order_by(
            '-intervention__intervention_date').first()
        state = None
        if intervention:
            state = intervention.station_state
        s.last_state = state
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0017_auto_20151204_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='stationsite',
            name='last_state',
            field=models.IntegerField(null=True, choices=[(1, 'En installation'), (7, 'En test'), (2, 'En opération'), (3, 'En défaillance'), (4, 'En panne'), (5, 'Fermée'), (6, 'Autre')], blank=True, verbose_name='État'),
        ),
        migrations.RunPython(migrate_last_station_state),
    ]
