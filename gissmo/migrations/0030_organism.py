# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def create_user(apps, string):
    User = apps.get_model('auth', 'User')
    username = string[:30]
    first_name = string[:30]
    last_name = ''
    separator = None
    if ' ' in string:
        separator = ' '
    if '.' in string:
        separator = '.'
    if separator:
        splits = string.split(separator)
        username = '.'.join(splits[:2]).lower()[:30]
        first_name = splits[0]
        last_name = splits[1]
        if len(splits) > 2:
            first_name = ' '.join(splits[:2])[:30]
            last_name = ' '.join(splits[2:])[:30]
        first_name = first_name.title()
        last_name = last_name.title()

    u = User.objects.create(
        username=username,
        is_active=False,
        first_name=first_name,
        last_name=last_name)
    return u


def check_and_create_organism(apps, ids, types):
    result = {}
    Actor = apps.get_model('gissmo', 'Actor')
    Organism = apps.get_model('gissmo', 'Organism')
    for actor in Actor.objects.filter(actor_type__in=ids):
        type_id = actor.actor_type
        name = actor.actor_name
        a = Organism.objects.filter(name__iexact=name).first()
        if not a:
            a = Organism.objects.create(
                name=name,
                _type=types[type_id])
        result[actor.id] = a
        # check parent organism
        if actor.actor_parent and actor.actor_parent.actor_name != name:
            parent_name = actor.actor_parent.actor_name
            organism = Organism.objects.filter(name=parent_name).first()
            if organism:
                a.parent = organism
                a.save()
    return result


def create_or_update_users(apps, ids, organisms):
    result = []
    Actor = apps.get_model('gissmo', 'Actor')
    User = apps.get_model('auth', 'User')
    for actor in Actor.objects.all().exclude(
            actor_type__in=ids):
        name = actor.actor_name
        parent = actor.actor_parent_id
        # check if name cannot be reduced as a login one (that exists)
        searched_name = name
        name_contains_space = False
        if ' ' in name:
            name_contains_space = True
            splits = name.split(' ')
            searched_name = name.replace(' ', '.').lower()
            # specific case
            if name == 'Hervé Wodling':
                searched_name = 'herve.wodling'

        u = User.objects.filter(username=searched_name).first()

        # update current user
        if u and name_contains_space and len(splits) == 2:
            u.first_name = splits[0]
            u.last_name = splits[1]
            u.save()

        if not u:
            u = create_user(apps, name)
        # link User to its organism
        if not parent or parent not in organisms.keys():
            if not u.groups.all():
                result.append(actor.actor_name)
            continue
        organisms[parent].users.add(u.id)


def migrate_groups_to_organism(apps, schema_editor):
    """
    Current groups are observatories (except Resif one).
    We so migrate groups to Organism, except Resif one.
    """
    Organism = apps.get_model('gissmo', 'Organism')
    Group = apps.get_model('auth', 'Group')
    for group in Group.objects.all():
        if group.name != 'Resif':
            Organism.objects.create(
                name=group.name,
                _type=0)  # Correspond to OBSERVATORY


def migrate_actors_to_organism_and_users(apps, schema_editor):
    """
    Each actor is either a User or an Organism. We migrate them to their
    new area.
    In case of User, we link it to its existing Organism.
    Notes:
      - username, first_name and last_name are limited to 30 chars
      - Actors with "Firstname Lastname" becomes "firstname.lastname" (User)
      - Actors with more than one word becomes "firstword.secondword" (User)
    """
    actor_non_physical = [
        1,  # OBSERVATOIRE
        3,  # ORGANISME
        4,  # ENTREPRISE
        5,  # ENTREPRISE SAV
        6]  # INCONNU
    actor_type_equivalent = {
        1: 0,  # OBSERVATORY
        3: 1,  # ORGANIZATION
        4: 2,  # BUSINESS
        5: 3,  # CUSTOMER SERVICE
        6: 4}  # UNKNOWN

    # first create organism (to be sure they exists for user
    # organism links)
    organisms = check_and_create_organism(
        apps,
        actor_non_physical,
        actor_type_equivalent)

    # Then we check all other one to link User to Organisms
    unaffiliated = create_or_update_users(
        apps,
        actor_non_physical,
        organisms)

    if unaffiliated:
        actors = ' '.join(unaffiliated)
        print('\nUser without any organism: %s' % actors)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gissmo', '0029_auto_20160308_1552'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('_type', models.IntegerField(default=4, verbose_name='Type', choices=[(0, 'Observatory/Laboratory'), (1, 'Organization'), (2, 'Business'), (3, 'Customer service Company'), (4, 'Unknown')])),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(to='gissmo.Organism', blank=True, null=True)),
            ],
        ),
        migrations.RunPython(migrate_groups_to_organism),
        migrations.RunPython(migrate_actors_to_organism_and_users),
    ]
