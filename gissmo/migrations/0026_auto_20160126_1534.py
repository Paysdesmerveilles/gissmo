# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import gissmo.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0025_auto_20160118_1029'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForbiddenEquipmentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('original', models.OneToOneField(verbose_name='Forbidden Model', to='gissmo.EquipModel')),
                ('recommended', models.ForeignKey(related_name='recommended_model', verbose_name='Recommended Model', to='gissmo.EquipModel')),
            ],
            options={
                'verbose_name': 'Forbidden Equipment Models',
                'verbose_name_plural': 'C2. Forbidden Equipment Models',
            },
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equip_model',
            field=models.ForeignKey(validators=[gissmo.validators.validate_equip_model], verbose_name="modele d'equipement", to='gissmo.EquipModel'),
        ),
    ]
