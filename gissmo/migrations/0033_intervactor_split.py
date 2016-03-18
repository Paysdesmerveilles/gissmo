# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def get_searched_name(string):
    result = string[:30]
    separator = None
    if ' ' in string:
        separator = ' '
    if '.' in string:
        separator = '.'
    if separator:
        splits = string.split(separator)
        result = '.'.join(splits[:2]).lower()[:30]
    return result


def create_intervorganism(apps, intervention, organism, note):
    """
    Only create IntervOrganism if no (Intervention and Organism) exists
    """
    IntervOrganism = apps.get_model('gissmo', 'IntervOrganism')
    exists = IntervOrganism.objects.filter(
        intervention=intervention,
        organism=organism)
    if not exists:
        IntervOrganism.objects.create(
            intervention=intervention,
            organism=organism,
            note=note)


def check_and_create_intervuser(apps, name, intervention, note):
    IntervUser = apps.get_model('gissmo', 'IntervUser')
    User = apps.get_model('auth', 'User')
    searched_name = get_searched_name(name)
    # Specific case
    if name == 'Hervé Wodling':
        searched_name = 'herve.wodling'
    u = User.objects.filter(username=searched_name).first()
    IntervUser.objects.create(
        intervention=intervention,
        user=u,
        note=note)
    # Search linked organism and create IntervOrganism
    for organism in u.organism_set.all():
        create_intervorganism(apps, intervention, organism, note)


def migrate_intervactor_to_user_and_organism(apps, schema_editor):
    IntervActor = apps.get_model('gissmo', 'IntervActor')
    Organism = apps.get_model('gissmo', 'Organism')

    actor_non_physical = [
        1,  # OBSERVATOIRE
        3,  # ORGANISME
        4,  # ENTREPRISE
        5,  # ENTREPRISE SAV
        6]  # INCONNU

    for i in IntervActor.objects.all().prefetch_related('actor'):
        name = i.actor.actor_name
        _type = i.actor.actor_type
        note = i.note
        intervention = i.intervention
        # Organism case (non physical actors)
        if _type in actor_non_physical:
            a = Organism.objects.filter(name=name).first()
            if not a:
                continue
            create_intervorganism(apps, intervention, a, note)
        # User case
        else:
            check_and_create_intervuser(apps, name, intervention, note)


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0032_auto_20160311_0922'),
    ]

    operations = [
        migrations.RunPython(migrate_intervactor_to_user_and_organism),
    ]
