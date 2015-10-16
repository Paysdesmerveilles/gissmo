# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def check_unknown_actor(apps, schema_editor):
    """
    Some actors needed:
      - Inconnu (StationSite form)
      - DT INSU (default owner on Equipment form)
    """
    # Actors (Intervenants)
    Actor = apps.get_model('gissmo', 'Actor')
    unknown_actors = Actor.objects.filter(actor_name='Inconnu', actor_type=6)
    if not unknown_actors:
        Actor.objects.create(
            actor_name='Inconnu',
            actor_type=6,
        )
    dt_insu_actors = Actor.objects.filter(actor_name='DT INSU', actor_type=1)
    if not dt_insu_actors:
        Actor.objects.create(
            actor_name='DT INSU',
            actor_type=1,
        )

class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0002_auto_20151012_1338'),
    ]

    operations = [
        migrations.RunPython(check_unknown_actor),
    ]
