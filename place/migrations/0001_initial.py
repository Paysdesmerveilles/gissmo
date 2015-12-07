# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=60, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('code', models.IntegerField(choices=[(0, 'Available'), (1, 'Used'), (2, 'Broken')])),
                ('start', models.DateTimeField(auto_now=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StateAvailable',
            fields=[
                ('state_ptr', models.OneToOneField(auto_created=True, to='place.State', parent_link=True, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('place.state',),
        ),
        migrations.CreateModel(
            name='StateBroken',
            fields=[
                ('state_ptr', models.OneToOneField(auto_created=True, to='place.State', parent_link=True, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('place.state',),
        ),
        migrations.CreateModel(
            name='StateUsed',
            fields=[
                ('state_ptr', models.OneToOneField(auto_created=True, to='place.State', parent_link=True, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('place.state',),
        ),
        migrations.AddField(
            model_name='state',
            name='polymorphic_ctype',
            field=models.ForeignKey(to='contenttypes.ContentType', related_name='polymorphic_place.state_set+', null=True, editable=False),
        ),
        migrations.AddField(
            model_name='state',
            name='site',
            field=models.ForeignKey(related_name='linked_site', to='place.Site'),
        ),
        migrations.AddField(
            model_name='site',
            name='state',
            field=models.ForeignKey(to='place.State', related_name='current_state', null=True),
        ),
    ]
