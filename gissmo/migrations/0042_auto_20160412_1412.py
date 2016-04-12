# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def add_default_ground_types(apps, schema_editor):
    GroundType = apps.get_model('gissmo', 'GroundType')
    GroundType.objects.get_or_create(
        name='A',
        description="Rock or other rock-like geological formation, including at most 5 m of weaker material at the surface.")
    GroundType.objects.get_or_create(
        name='B',
        description="Deposits of very dense sand, gravel, or very stiff clay, at least several tens of meters in thickness, characterized by a gradual increase of mechanical properties with depth.")
    GroundType.objects.get_or_create(
        name='C',
        description="Deep deposits of dense or medium dense sand, gravel or stiff clay with thickness from several tens to many hundreds of meters.")
    GroundType.objects.get_or_create(
        name='D',
        description="Deposits of loose-to-medium cohesionless soil (with or without some soft cohesive layers), or of predominantly soft-to-firm cohesive soil.")
    GroundType.objects.get_or_create(
        name='E',
        description="A soil profile consisting of a surface alluvium layer with vs values of type C or D and thickness varying between about 5 m and 20 m, underlain by stiffer material with vs > 800 m/s.")
    GroundType.objects.get_or_create(
        name='S1',
        description="Deposits consisting, or containing a layer at least 10 m thick, of soft clays/silts with a high plasticity index (PI > 40) and high water content")
    GroundType.objects.get_or_create(
        name='S2',
        description="Deposits of liquefiable soils, of sensitive clays, or any other soil profile not included in types A – E or S1")


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0041_auto_20160412_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroundType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=2, unique=True)),
                ('description', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'EC8 Soil classification',
            },
        ),
        migrations.AddField(
            model_name='stationsite',
            name='ground_type',
            field=models.ForeignKey(null=True, verbose_name='EC8 Soil classification', blank=True, to='gissmo.GroundType'),
        ),
        migrations.RunPython(add_default_ground_types),
    ]
