# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-21 15:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('document', '0001_initial'),
        ('place', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(db_index=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('confirmed', models.BooleanField(default=None)),
                ('documents', models.ManyToManyField(blank=True, to='document.Document')),
                ('operators', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='place.Site')),
            ],
        ),
    ]
