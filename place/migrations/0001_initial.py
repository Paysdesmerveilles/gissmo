# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-22 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('affiliation', '0001_initial'),
        ('document', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroundType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2, unique=True)),
                ('description', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'EC8 Soil classification',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('_type', models.IntegerField(choices=[(0, 'Unknown'), (1, 'Agency'), (2, 'Theoritical site'), (3, 'Measuring site'), (4, 'Customer service place'), (5, 'Tunnel'), (6, 'Drift'), (7, 'Drain'), (8, 'Cave'), (9, 'Underground'), (10, 'Cabinet'), (11, 'Chamber'), (12, 'Prefabricated'), (13, 'Premises'), (14, 'Fort'), (15, 'Apron'), (16, 'Slab'), (17, 'Outside'), (18, 'Well'), (19, 'Drilling')], default=0, verbose_name='Type')),
                ('description', models.TextField(blank=True, null=True)),
                ('creation_date', models.DateField(blank=True, null=True, verbose_name='Creation date')),
                ('note', models.TextField(blank=True, null=True)),
                ('address_street', models.CharField(blank=True, max_length=100, null=True, verbose_name='Street')),
                ('address_zipcode', models.CharField(blank=True, max_length=15, null=True, verbose_name='Zip code')),
                ('address_city', models.CharField(blank=True, max_length=100, null=True, verbose_name='City')),
                ('address_region', models.CharField(blank=True, max_length=100, null=True, verbose_name='Region')),
                ('address_county', models.CharField(blank=True, max_length=100, null=True, verbose_name='District')),
                ('address_country', models.CharField(blank=True, max_length=50, null=True, verbose_name='Country')),
                ('geology', models.CharField(blank=True, max_length=50, null=True, verbose_name='Geological formation')),
                ('contact', models.TextField(blank=True, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Latitude (°)')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Longitude (°)')),
                ('elevation', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True, verbose_name='Elevation (m)')),
            ],
        ),
        migrations.CreateModel(
            name='PlaceDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='document.Document')),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='place.Place')),
            ],
        ),
        migrations.AddField(
            model_name='place',
            name='documents',
            field=models.ManyToManyField(blank=True, through='place.PlaceDocument', to='document.Document'),
        ),
        migrations.AddField(
            model_name='place',
            name='ground_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='place.GroundType', verbose_name='EC8 Soil classification'),
        ),
        migrations.AddField(
            model_name='place',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='affiliation.Organism'),
        ),
        migrations.AddField(
            model_name='place',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='place.Place', verbose_name='Referent place'),
        ),
    ]
