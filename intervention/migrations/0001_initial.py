# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('place', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionEquipment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('note', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'intervention on equipment',
                'verbose_name_plural': 'Equipment interventions',
            },
        ),
        migrations.CreateModel(
            name='ActionSite',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('transition', models.IntegerField(choices=[(0, 'Test failed'), (1, 'Test succeeded'), (2, 'Have a failure'), (3, 'Fixed')])),
                ('note', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'intervention on site',
                'verbose_name_plural': 'Site interventions',
            },
        ),
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(db_index=True)),
                ('note', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='InterventionPlayer',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('intervention', models.ForeignKey(to='intervention.Intervention')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='interventionplayer',
            name='player',
            field=models.ForeignKey(to='intervention.Player'),
        ),
        migrations.AddField(
            model_name='intervention',
            name='players',
            field=models.ManyToManyField(through='intervention.InterventionPlayer', to='intervention.Player'),
        ),
        migrations.AddField(
            model_name='intervention',
            name='site',
            field=models.ForeignKey(to='place.Site'),
        ),
        migrations.AddField(
            model_name='actionsite',
            name='intervention',
            field=models.ForeignKey(to='intervention.Intervention'),
        ),
        migrations.AddField(
            model_name='actionequipment',
            name='intervention',
            field=models.ForeignKey(to='intervention.Intervention'),
        ),
    ]
