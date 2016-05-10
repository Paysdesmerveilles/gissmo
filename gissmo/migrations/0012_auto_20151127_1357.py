# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_last_equipment_state(apps, schema_editor):
    """
    All equipments' statuses are in IntervEquip.
    We now have a specific field in Equipment to know the last one: last_state
    So we need to copy the last known value from IntervEquip to Equipment.
    """
    Equipment = apps.get_model('gissmo', 'Equipment')
    equipments = Equipment.objects.all().prefetch_related(
        'intervequip_set__intervention')
    for e in equipments:
        intervention = e.intervequip_set.filter(
            equip_state__isnull=False).order_by(
            'intervention__intervention_date')[:1].last()
        state = None
        if intervention:
            state = intervention.equip_state
        e.last_state = state
        e.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0011_stationsite_creation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='last_state',
            field=models.IntegerField(choices=[(1, 'En opération'), (2, 'A tester'), (3, 'Disponible'), (4, 'En défaillance'), (5, 'En panne'), (6, 'En transit'), (7, "Hors d'usage"), (8, 'Disparu'), (9, 'Au rebut'), (10, 'Autre')], blank=True, verbose_name='État', null=True),
        ),
        migrations.AlterModelOptions(
            name='equipstate',
            options={'managed': False},
        ),
        migrations.RunPython(migrate_last_equipment_state),
    ]
