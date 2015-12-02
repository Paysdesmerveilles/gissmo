# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_last_equipment_station(apps, schema_editor):
    """
    All equipments' stations are in IntervEquip.
    We now have a specific field in Equipment to know the last one:
    last_station.
    So we need to copy the last known value from IntervEquip to Equipment.
    """
    Equipment = apps.get_model('gissmo', 'Equipment')
    equipments = Equipment.objects.all().prefetch_related(
        'intervequip_set__intervention')
    for e in equipments:
        intervention = e.intervequip_set.filter(
            station__isnull=False).order_by(
            '-intervention__intervention_date').first()
        station = None
        if intervention:
            station = intervention.station
        e.last_station = station
        e.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0013_auto_20151130_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='last_station',
            field=models.ForeignKey(to='gissmo.StationSite', null=True, verbose_name='Emplacement', blank=True),
        ),
        migrations.RunPython(migrate_last_equipment_station),
    ]
