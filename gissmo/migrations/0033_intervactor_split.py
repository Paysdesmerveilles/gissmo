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


def create_intervaffiliation(apps, intervention, affiliation, note):
    """
    Only create IntervAffiliation if no (Intervention and Affiliation) exists
    """
    IntervAffiliation = apps.get_model('gissmo', 'IntervAffiliation')
    exists = IntervAffiliation.objects.filter(
        intervention=intervention,
        affiliation=affiliation)
    if not exists:
        IntervAffiliation.objects.create(
            intervention=intervention,
            affiliation=affiliation,
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
    # Search linked affiliation and create IntervAffiliation
    for affiliation in u.affiliation_set.all():
        create_intervaffiliation(apps, intervention, affiliation, note)


def migrate_intervactor_to_user_and_affiliation(apps, schema_editor):
    IntervActor = apps.get_model('gissmo', 'IntervActor')
    Affiliation = apps.get_model('gissmo', 'Affiliation')

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
        # Affiliation case (non physical actors)
        if _type in actor_non_physical:
            a = Affiliation.objects.filter(name=name).first()
            if not a:
                continue
            create_intervaffiliation(apps, intervention, a, note)
        # User case
        else:
            check_and_create_intervuser(apps, name, intervention, note)


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0032_auto_20160311_0922'),
    ]

    operations = [
        migrations.RunPython(migrate_intervactor_to_user_and_affiliation),
    ]
