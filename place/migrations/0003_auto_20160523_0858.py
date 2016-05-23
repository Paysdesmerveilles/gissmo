# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('affiliation', '0001_initial'),
        ('place', '0002_auto_20160502_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaceOperator',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('operator', models.ForeignKey(to='affiliation.Agency')),
            ],
        ),
        migrations.RemoveField(
            model_name='place',
            name='operator',
        ),
        migrations.AddField(
            model_name='placeoperator',
            name='place',
            field=models.ForeignKey(to='place.Place'),
        ),
        migrations.AddField(
            model_name='place',
            name='operators',
            field=models.ManyToManyField(blank=True, to='affiliation.Agency', through='place.PlaceOperator'),
        ),
    ]
