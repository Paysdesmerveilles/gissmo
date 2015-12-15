# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_built_name(apps, schema_editor):
    """
    In a given station, each built type cannot have twice the same built name.
    We so rename each existing built to be "Unknown" + a number.
    The number is given by the count of each built in a given built type.
    """
    Built = apps.get_model('gissmo', 'Built')
    Station = apps.get_model('gissmo', 'StationSite')
    BuiltType = apps.get_model('gissmo', 'BuiltType')
    stations = Station.objects.all()
    for s in stations:
        for t in BuiltType.objects.all():
            builts = Built.objects.filter(
                station_id=s.id,
                built_short_desc__isnull=True,
                built_type_id=t.id)
            builts_ids = [b.id for b in builts]
            if len(builts) > 1:
                for b_id in builts_ids:
                    b_obj = Built.objects.get(pk=b_id)
                    b_obj.built_short_desc = "%s%s" % (
                        "Unknown",
                        builts_ids.index(b_id))
                    b_obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0012_auto_20151127_1357'),
    ]

    operations = [
        migrations.RunPython(migrate_built_name),
        migrations.AlterField(
            model_name='built',
            name='built_short_desc',
            field=models.CharField(max_length=40, verbose_name='courte description', default='Unknown'),
        ),

    ]
