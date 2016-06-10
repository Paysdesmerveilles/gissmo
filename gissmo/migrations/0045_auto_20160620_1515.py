# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_equipments(apps, schema_editor):
    """
    Create default configuration for equipments whose model have parameters.
    """
    Model = apps.get_model('gissmo', 'EquipModel')
    Config = apps.get_model('gissmo', 'ConfigEquip')
    Parameter = apps.get_model('gissmo', 'ParameterEquip')

    # Only process models that have some parameters
    models = Parameter.objects.all().values(
        'equip_model_id').distinct().order_by('equip_model_id')

    for model_data in models:
        m = Model.objects.get(pk=model_data.get('equip_model_id'))
        # keep params/value for each model
        model_config = {}
        for p in m.parameterequip_set.all():
            # check if a default_value exists
            have_default = p.parametervalue_set.filter(
                default_value=True).count()
            if have_default:
                val = p.parametervalue_set.filter(default_value=True).first()
            else:
                val = p.parametervalue_set.first()
            model_config[p] = val

        # apply this configuration to each linked equipment
        for e in m.equipment_set.all():
            for param in model_config:
                Config.objects.create(
                    equipment=e,
                    parameter=param,
                    value=model_config[param])


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0044_auto_20160509_0858'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigEquip',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('equipment', models.ForeignKey(to='gissmo.Equipment')),
                ('parameter', models.ForeignKey(to='gissmo.ParameterEquip')),
                ('value', models.ForeignKey(to='gissmo.ParameterValue', verbose_name='Value')),
            ],
            options={
                'verbose_name': 'Configuration',
            },
        ),
        migrations.AddField(
            model_name='equipment',
            name='configurations',
            field=models.ManyToManyField(to='gissmo.ParameterEquip', through='gissmo.ConfigEquip'),
        ),
        migrations.RunPython(migrate_equipments),
    ]
