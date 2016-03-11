# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gissmo', '0031_station_and_equipment_rename'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntervAffiliation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('note', models.TextField(null=True, blank=True)),
                ('affiliation', models.ForeignKey(to='gissmo.Affiliation')),
                ('intervention', models.ForeignKey(to='gissmo.Intervention')),
            ],
            options={
                'verbose_name': 'Operator',
            },
        ),
        migrations.CreateModel(
            name='IntervUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('note', models.TextField(null=True, blank=True)),
                ('intervention', models.ForeignKey(to='gissmo.Intervention')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Protagonist',
            },
        ),
        migrations.AddField(
            model_name='intervention',
            name='affiliations',
            field=models.ManyToManyField(to='gissmo.Affiliation', through='gissmo.IntervAffiliation'),
        ),
        migrations.AddField(
            model_name='intervention',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='gissmo.IntervUser'),
        ),
    ]
