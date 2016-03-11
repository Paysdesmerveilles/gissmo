# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_equipment_owner_to_user_id(apps, schema_editor):
    Equipment = apps.get_model('gissmo', 'Equipment')
    Affiliation = apps.get_model('gissmo', 'Affiliation')
    correlation = {}
    for e in Equipment.objects.all():
        search_name = 'Inconnu'
        if e.owner:
            search_name = e.owner.actor_name
        affiliation = Affiliation.objects.filter(name=search_name).first()
        correlation[e.id] = affiliation.id
    for e_id in correlation:
        e = Equipment.objects.get(pk=e_id)
        e.owner_id = correlation[e_id]
        e.save()


def migrate_stationsite_operator_to_user_id(apps, schema_editor):
    StationSite = apps.get_model('gissmo', 'StationSite')
    Affiliation = apps.get_model('gissmo', 'Affiliation')
    correlation = {}
    for s in StationSite.objects.all():
        search_name = 'Inconnu'
        if s.operator:
            search_name = s.operator.actor_name
        affiliation = Affiliation.objects.filter(name=search_name).first()
        correlation[s.id] = affiliation.id
    for s_id in correlation:
        s = StationSite.objects.get(pk=s_id)
        s.operator_id = affiliation.id
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0030_affiliation'),
    ]

    operations = [
        migrations.RunPython(migrate_equipment_owner_to_user_id),
        migrations.RunPython(migrate_stationsite_operator_to_user_id),
    ]
