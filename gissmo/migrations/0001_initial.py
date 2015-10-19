# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields
import gissmo.models
from django.conf import settings
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoggedActions',
            fields=[
                ('event_id', models.BigIntegerField(
                    serialize=False,
                    primary_key=True)),
                ('schema_name', models.TextField()),
                ('table_name', models.TextField()),
                ('relid', models.TextField()),
                ('session_user_name', models.TextField(blank=True)),
                ('action_tstamp_tx', models.DateTimeField()),
                ('action_tstamp_stm', models.DateTimeField()),
                ('action_tstamp_clk', models.DateTimeField()),
                ('transaction_id', models.BigIntegerField(
                    null=True,
                    blank=True)),
                ('application_name', models.TextField(blank=True)),
                ('client_addr', models.GenericIPAddressField(
                    null=True,
                    blank=True)),
                ('client_port', models.IntegerField(null=True, blank=True)),
                ('client_query', models.TextField()),
                ('action', models.TextField()),
                ('row_data', models.TextField()),
                ('changed_fields', models.TextField()),
                ('statement_only', models.BooleanField()),
            ],
            options={
                'db_table': 'logged_actions',
                'managed': False,
                'verbose_name_plural': 'Logged actions',
            },
        ),
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('actor_type', models.IntegerField(
                    default=7,
                    verbose_name="Type d'intervenant",
                    choices=[
                        (1, b'Observatoire/Laboratoire'),
                        (2, b'Ing\xc3\xa9nieur/Technicien'),
                        (3, b'R\xc3\xa9seau'),
                        (4, b'Entreprise'),
                        (5, b'Entreprise SAV'),
                        (6, b'Inconnu'),
                        (7, b'Autre')])),
                ('actor_name', models.CharField(
                    unique=True,
                    max_length=50,
                    verbose_name='nom')),
                ('actor_note', models.TextField(
                    null=True,
                    verbose_name='note',
                    blank=True)),
                ('actor_parent', models.ForeignKey(
                    verbose_name="Groupe d'appartenance",
                    blank=True,
                    to='gissmo.Actor',
                    null=True)),
            ],
            options={
                'ordering': ['actor_name'],
                'verbose_name': 'intervenant',
                'verbose_name_plural': 'F1. Intervenants',
            },
        ),
        migrations.CreateModel(
            name='Built',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('built_short_desc', models.CharField(
                    max_length=40,
                    null=True,
                    verbose_name='courte description',
                    blank=True)),
                ('built_note', models.TextField(
                    null=True,
                    verbose_name='note',
                    blank=True)),
            ],
            options={
                'verbose_name': 'bati',
                'verbose_name_plural': 'B1. Batis',
            },
        ),
        migrations.CreateModel(
            name='BuiltType',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('built_type_name', models.CharField(
                    max_length=40,
                    verbose_name='type de bati')),
            ],
            options={
                'ordering': ['built_type_name'],
                'verbose_name': 'type de bati',
                'verbose_name_plural': 'T1. Types of building',
            },
        ),
        migrations.CreateModel(
            name='CalibrationUnit',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('name', models.CharField(
                    max_length=50,
                    verbose_name='Nom unite')),
                ('description', models.TextField(
                    null=True,
                    verbose_name='description',
                    blank=True)),
            ],
            options={
                'verbose_name_plural': 'U1. Types of unit',
            },
        ),
        migrations.CreateModel(
            name='Chain',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('order', models.IntegerField(
                    verbose_name='Type',
                    choices=[
                        (1, b'Sensor'),
                        (2, b'PreAmplifier'),
                        (3, b'DataLogger'),
                        (4, b'Equipment'),
                        (5, b'Other_1'),
                        (6, b'Other_2'),
                        (7, b'Other_3'),
                        (7, b'Other_4'),
                        (9, b'Other_5')])),
            ],
            options={
                'verbose_name': "Composante de la chaine d'acqui",
                'verbose_name_plural': "Z2. Composantes des chaines d'acqui",
            },
        ),
        migrations.CreateModel(
            name='ChainConfig',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('chain', models.ForeignKey(
                    verbose_name="chaine d'acquisition",
                    to='gissmo.Chain')),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('location_code', models.CharField(
                    max_length=2,
                    null=True,
                    verbose_name='code localisation',
                    blank=True)),
                ('latitude', models.DecimalField(
                    verbose_name='latitude (degre decimal)',
                    max_digits=8,
                    decimal_places=6)),
                ('longitude', models.DecimalField(
                    verbose_name='longitude (degre decimal)',
                    max_digits=9,
                    decimal_places=6)),
                ('elevation', models.DecimalField(
                    verbose_name='elevation (m)',
                    max_digits=5,
                    decimal_places=1)),
                ('depth', models.DecimalField(
                    verbose_name='profondeur (m)',
                    max_digits=4,
                    decimal_places=1)),
                ('azimuth', models.DecimalField(
                    verbose_name='azimut',
                    max_digits=4,
                    decimal_places=1)),
                ('dip', models.DecimalField(
                    verbose_name="angle d'inclinaison",
                    max_digits=3,
                    decimal_places=1)),
                ('sample_rate', models.FloatField(
                    verbose_name='frequence (Hz)')),
                ('start_date', models.DateTimeField(
                    verbose_name='date debut (aaaa-mm-jj)')),
                ('end_date', models.DateTimeField(
                    null=True,
                    verbose_name='date fin (aaaa-mm-jj)',
                    blank=True)),
                ('restricted_status', models.IntegerField(
                    blank=True,
                    null=True,
                    verbose_name='etat restrictif',
                    choices=[
                        (1, b'Ouvert'),
                        (2, b'Ferme'),
                        (3, b'Partiel')])),
                ('alternate_code', models.CharField(
                    max_length=5,
                    null=True,
                    verbose_name='code alternatif',
                    blank=True)),
                ('historical_code', models.CharField(
                    max_length=5,
                    null=True,
                    verbose_name='code historique',
                    blank=True)),
                ('description', models.TextField(
                    null=True,
                    verbose_name='description',
                    blank=True)),
                ('storage_format', models.CharField(
                    max_length=50,
                    null=True,
                    verbose_name='format de donnees',
                    blank=True)),
                ('clock_drift', models.FloatField(
                    null=True,
                    verbose_name='derive horloge (seconds/sample)',
                    blank=True)),
                ('latitude_unit', models.CharField(
                    default=b'DEGREES',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('latitude_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('latitude_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('latitude_datum', models.CharField(
                    default=b'WSG84',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('longitude_unit', models.CharField(
                    default=b'DEGREES',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('longitude_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('longitude_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('longitude_datum', models.CharField(
                    default=b'WSG84',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('elevation_unit', models.CharField(
                    default=b'METERS',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('elevation_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('elevation_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('depth_unit', models.CharField(
                    default=b'METERS',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('depth_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('depth_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('azimuth_unit', models.CharField(
                    default=b'DEGREES',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('azimuth_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('azimuth_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('dip_unit', models.CharField(
                    default=b'DEGREES',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('dip_pluserror', models.FloatField(null=True, blank=True)),
                ('dip_minuserror', models.FloatField(null=True, blank=True)),
                ('sample_rate_unit', models.CharField(
                    default=b'SAMPLES/S',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('sample_rate_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('sample_rate_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('clock_drift_unit', models.CharField(
                    default=b'SECONDS/SAMPLE',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('clock_drift_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('clock_drift_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('calibration_units', models.ForeignKey(
                    verbose_name='unite de mesure',
                    blank=True,
                    to='gissmo.CalibrationUnit',
                    null=True)),
            ],
            options={
                'verbose_name': "Canal d'acquisition",
                'verbose_name_plural': "Z1. Canaux d'acquisition",
            },
        ),
        migrations.CreateModel(
            name='ChannelCode',
            fields=[
                ('channel_code', models.CharField(
                    max_length=3,
                    serialize=False,
                    verbose_name='code du canal',
                    primary_key=True)),
                ('presentation_rank', models.IntegerField(
                    null=True,
                    blank=True)),
                ('validation_rule', models.TextField(
                    null=True,
                    verbose_name='regle validation',
                    blank=True)),
            ],
            options={
                'verbose_name': 'Code du canal',
                'verbose_name_plural': 'Z3. Codes des canaux',
            },
        ),
        migrations.CreateModel(
            name='CommentChannel',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('value', models.TextField(verbose_name='commentaire')),
                ('begin_effective', models.DateTimeField(
                    null=True,
                    verbose_name='debut effectivite (aaaa-mm-jj)',
                    blank=True)),
                ('end_effective', models.DateTimeField(
                    null=True,
                    verbose_name='fin effectivite (aaaa-mm-jj)',
                    blank=True)),
                ('channel', models.ForeignKey(
                    verbose_name='canal',
                    to='gissmo.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='CommentChannelAuthor',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('author', models.ForeignKey(
                    verbose_name='auteur',
                    to='gissmo.Actor')),
                ('comment_channel', models.ForeignKey(
                    verbose_name='commentaire',
                    to='gissmo.CommentChannel')),
            ],
        ),
        migrations.CreateModel(
            name='CommentNetwork',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('value', models.TextField(verbose_name='commentaire')),
                ('begin_effective', models.DateTimeField(
                    null=True,
                    verbose_name='debut effectivite (aaaa-mm-jj)',
                    blank=True)),
                ('end_effective', models.DateTimeField(
                    null=True,
                    verbose_name='fin effectivite (aaaa-mm-jj)',
                    blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommentNetworkAuthor',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('author', models.ForeignKey(
                    verbose_name='auteur',
                    to='gissmo.Actor')),
                ('comment_network', models.ForeignKey(
                    verbose_name='commentaire',
                    to='gissmo.CommentNetwork')),
            ],
        ),
        migrations.CreateModel(
            name='CommentStationSite',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('value', models.TextField(verbose_name='commentaire')),
                ('begin_effective', models.DateTimeField(
                    null=True,
                    verbose_name='debut effectivite (aaaa-mm-jj)',
                    blank=True)),
                ('end_effective', models.DateTimeField(
                    null=True,
                    verbose_name='fin effectivite (aaaa-mm-jj)',
                    blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommentStationSiteAuthor',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('author', models.ForeignKey(
                    verbose_name='auteur',
                    to='gissmo.Actor')),
                ('comment_station', models.ForeignKey(
                    verbose_name='commentaire',
                    to='gissmo.CommentStationSite')),
            ],
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('type_description', models.CharField(
                    max_length=50,
                    verbose_name='type de donnees')),
            ],
            options={
                'verbose_name_plural': 'V1. Types of collected data',
            },
        ),
        migrations.CreateModel(
            name='EquipAction',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('equip_action_name', models.CharField(
                    max_length=50,
                    null=True,
                    blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='EquipDoc',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('document_title', models.CharField(
                    max_length=40,
                    verbose_name='titre document')),
                ('inscription_date', models.DateField(
                    null=True,
                    verbose_name='date inscription (aaaa-mm-jj)',
                    blank=True)),
                ('document_equip', models.FileField(
                    upload_to=gissmo.models.equipdoc_file_name,
                    storage=django.core.files.storage.FileSystemStorage(
                        location=b'/home/olivier/gissmo/upload'),
                    verbose_name='document',
                    blank=True)),
                ('private_link', models.URLField(
                    null=True,
                    verbose_name='lien document prive',
                    blank=True)),
                ('begin_effective', models.DateField(
                    null=True,
                    verbose_name='debut effectivite (aaaa-mm-jj)',
                    blank=True)),
                ('end_effective', models.DateField(
                    null=True,
                    verbose_name='fin effectivite (aaaa-mm-jj)',
                    blank=True)),
            ],
            options={
                'verbose_name': "Document de l'equipement",
                'verbose_name_plural': 'G3. Documents des equipements',
            },
        ),
        migrations.CreateModel(
            name='EquipDocType',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('equipdoc_type_name', models.CharField(
                    max_length=40,
                    verbose_name='type de document')),
            ],
            options={
                'verbose_name_plural': 'R1. Types of document (equipment)',
            },
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('serial_number', models.CharField(
                    max_length=50,
                    verbose_name='numero de serie')),
                ('vendor', models.CharField(
                    max_length=50,
                    null=True,
                    verbose_name='vendeur',
                    blank=True)),
                ('contact', models.TextField(
                    null=True,
                    verbose_name='contact',
                    blank=True)),
                ('note', models.TextField(
                    null=True,
                    verbose_name='note',
                    blank=True)),
            ],
            options={
                'verbose_name': 'equipement',
                'verbose_name_plural': 'D1. Equipements',
            },
        ),
        migrations.CreateModel(
            name='EquipModel',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('equip_model_name', models.CharField(
                    max_length=50,
                    verbose_name="modele d'equipement")),
                ('manufacturer', models.CharField(
                    max_length=50,
                    null=True,
                    verbose_name='manufacturier',
                    blank=True)),
            ],
            options={
                'ordering': ['equip_model_name'],
                'verbose_name': "modele d'equipement",
                'verbose_name_plural': 'C1. Modeles des equipements',
            },
        ),
        migrations.CreateModel(
            name='EquipModelDoc',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('document_title', models.CharField(
                    max_length=40,
                    verbose_name='titre document')),
                ('inscription_date', models.DateField(
                    null=True,
                    verbose_name='date inscription (aaaa-mm-jj)',
                    blank=True)),
                ('document_equip_model', models.FileField(
                    upload_to=gissmo.models.equipmodeldoc_file_name,
                    storage=django.core.files.storage.FileSystemStorage(
                        location=b'/home/olivier/gissmo/upload'),
                    verbose_name='document',
                    blank=True)),
                ('private_link', models.URLField(
                    null=True,
                    verbose_name='lien document prive',
                    blank=True)),
                ('begin_effective', models.DateField(
                    null=True,
                    verbose_name='debut effectivite (aaaa-mm-jj)',
                    blank=True)),
                ('end_effective', models.DateField(
                    null=True,
                    verbose_name='fin effectivite (aaaa-mm-jj)',
                    blank=True)),
            ],
            options={
                'verbose_name': "Document du modele d'equipement",
                'verbose_name_plural':
                    "G2. Documents des modeles d'equipement",
            },
        ),
        migrations.CreateModel(
            name='EquipModelDocType',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('equipmodeldoc_type_name', models.CharField(
                    max_length=40,
                    verbose_name='type de document')),
            ],
            options={
                'verbose_name_plural': 'Q1. Types of document (equip. model)',
            },
        ),
        migrations.CreateModel(
            name='EquipState',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('equip_state_name', models.CharField(
                    max_length=50,
                    null=True,
                    blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='EquipSupertype',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('equip_supertype_name', models.CharField(
                    max_length=40,
                    verbose_name="supertype d'equipement")),
                ('presentation_rank', models.IntegerField()),
            ],
            options={
                'ordering': ['equip_supertype_name'],
                'verbose_name': "supertype de l'equipement",
                'verbose_name_plural': 'supertypes des equipements',
            },
        ),
        migrations.CreateModel(
            name='EquipType',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('equip_type_name', models.CharField(
                    max_length=40,
                    verbose_name="type d'equipement")),
                ('presentation_rank', models.IntegerField()),
                ('equip_supertype', models.ForeignKey(
                    verbose_name="supertype d'equipement",
                    to='gissmo.EquipSupertype')),
            ],
            options={
                'ordering': ['equip_type_name'],
                'verbose_name': "type d'equipement",
                'verbose_name_plural': 'types des equipements',
            },
        ),
        migrations.CreateModel(
            name='IntervActor',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('note', models.TextField(
                    null=True,
                    verbose_name='note',
                    blank=True)),
                ('actor', models.ForeignKey(
                    verbose_name='intervenant',
                    to='gissmo.Actor')),
            ],
            options={
                'verbose_name_plural': 'Intervenants',
            },
        ),
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('intervention_date', models.DateTimeField(
                    verbose_name='date (aaaa-mm-jj)')),
                ('note', models.TextField(
                    null=True,
                    verbose_name='note',
                    blank=True)),
            ],
            options={
                'verbose_name': 'Intervention',
                'verbose_name_plural': 'E1. Interventions',
            },
        ),
        migrations.CreateModel(
            name='IntervEquip',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('equip_action', models.IntegerField(
                    verbose_name='action',
                    choices=[
                        (1, b'Acheter'),
                        (2, b'Tester'),
                        (3, b'Installer'),
                        (4, b'D\xc3\xa9sinstaller'),
                        (5, b'Constater d\xc3\xa9faut'),
                        (6, b'Effectuer maintenance pr\xc3\xa9ventive \
\xc3\xa0 distance'),
                        (7, b'Effectuer maintenance corrective \xc3\xa0 \
distance'),
                        (8, b'Effectuer maintenance pr\xc3\xa9ventive sur \
site'),
                        (9, b'Effectuer maintenance corrective sur site'),
                        (10, b'Exp\xc3\xa9dier'),
                        (11, b'Recevoir'),
                        (12, b'Mettre hors usage'),
                        (13, b'Constater disparition'),
                        (14, b'Retrouver suite \xc3\xa0 une disparition'),
                        (15, b'Mettre au rebut'),
                        (16, b'Autre')])),
                ('equip_state', models.IntegerField(
                    verbose_name='etat',
                    choices=[
                        (1, b'En op\xc3\xa9ration'),
                        (2, b'A tester'),
                        (3, b'Disponible'),
                        (4, b'En d\xc3\xa9faillance'),
                        (5, b'En panne'),
                        (6, b'En transit'),
                        (7, b"Hors d'usage"),
                        (8, b'Disparu'),
                        (9, b'Au rebut'),
                        (10, b'Autre')])),
                ('note', models.TextField(
                    null=True,
                    verbose_name='note',
                    blank=True)),
                ('built', models.ForeignKey(
                    verbose_name='bati',
                    blank=True,
                    to='gissmo.Built',
                    null=True)),
                ('equip', models.ForeignKey(
                    verbose_name='equipement',
                    to='gissmo.Equipment')),
                ('intervention', models.ForeignKey(
                    verbose_name='intervention',
                    to='gissmo.Intervention')),
            ],
            options={
                'verbose_name_plural': 'Actions sur les equipements',
            },
        ),
        migrations.CreateModel(
            name='IntervStation',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('station_action', models.IntegerField(
                    verbose_name='action',
                    choices=[
                        (1, b'Cr\xc3\xa9er code station'),
                        (2, b'Installer station'),
                        (11, b'D\xc3\xa9buter test'),
                        (12, b'Terminer test'),
                        (3, b'Mettre en op\xc3\xa9ration'),
                        (4, b'Constater d\xc3\xa9faillance'),
                        (5, b'Effectuer maintenance pr\xc3\xa9ventive \
\xc3\xa0 distance'),
                        (6, b'Effectuer maintenance corrective \xc3\xa0 \
distance'),
                        (7, b'Effectuer maintenance pr\xc3\xa9ventive \
sur site'),
                        (8, b'Effectuer maintenance corrective sur site'),
                        (9, b'D\xc3\xa9manteler'),
                        (10, b'Autre')])),
                ('station_state', models.IntegerField(
                    blank=True,
                    null=True,
                    verbose_name='etat',
                    choices=[
                        (1, b'En installation'),
                        (7, b'En test'),
                        (2, b'En op\xc3\xa9ration'),
                        (3, b'En d\xc3\xa9faillance'),
                        (4, b'En panne'),
                        (5, b'Ferm\xc3\xa9e'),
                        (6, b'Autre')])),
                ('note', models.TextField(
                    null=True,
                    verbose_name='note',
                    blank=True)),
                ('intervention', models.ForeignKey(
                    verbose_name='intervention',
                    to='gissmo.Intervention')),
            ],
            options={
                'verbose_name_plural': 'Actions sur le site',
            },
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('network_code', models.CharField(
                    max_length=5,
                    verbose_name='network code')),
                ('network_name', models.CharField(
                    max_length=50,
                    null=True,
                    verbose_name='nom du reseau',
                    blank=True)),
                ('code', models.CharField(
                    max_length=5,
                    verbose_name='code reseau')),
                ('start_date', models.DateTimeField(
                    null=True,
                    verbose_name='date debut (aaaa-mm-jj)',
                    blank=True)),
                ('end_date', models.DateTimeField(
                    null=True,
                    verbose_name='date fin (aaaa-mm-jj)',
                    blank=True)),
                ('restricted_status', models.IntegerField(
                    blank=True,
                    null=True,
                    verbose_name='etat restrictif',
                    choices=[
                        (1, b'Ouvert'),
                        (2, b'Ferme'),
                        (3, b'Partiel')])),
                ('alternate_code', models.CharField(
                    max_length=5,
                    null=True,
                    verbose_name='code alternatif',
                    blank=True)),
                ('historical_code', models.CharField(
                    max_length=5,
                    null=True,
                    verbose_name='code historique',
                    blank=True)),
                ('description', models.TextField(
                    null=True,
                    verbose_name='description',
                    blank=True)),
            ],
            options={
                'verbose_name': 'reseau',
                'verbose_name_plural': 'N1. Reseaux',
            },
        ),
        migrations.CreateModel(
            name='ParameterEquip',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('parameter_name', models.CharField(
                    max_length=50,
                    verbose_name='nom du parametre')),
                ('equip_model', models.ForeignKey(
                    verbose_name="modele d'equipement",
                    to='gissmo.EquipModel')),
            ],
            options={
                'verbose_name': 'parametre equip',
                'verbose_name_plural': 'W1. Parametres equip',
            },
        ),
        migrations.CreateModel(
            name='ParameterValue',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('value', models.CharField(
                    max_length=50,
                    verbose_name='valeur')),
                ('default_value', models.BooleanField(
                    verbose_name='valeur par defaut')),
                ('parameter', models.ForeignKey(
                    verbose_name="Parametre modele d'equipement",
                    to='gissmo.ParameterEquip')),
            ],
            options={
                'verbose_name': 'valeur du parametre',
                'verbose_name_plural': 'X1. Valeurs des parametres',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False, auto_created=True, primary_key=True)),
                ('project_name', models.CharField(max_length=50)),
                ('manager', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUser',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('project', models.ManyToManyField(to='gissmo.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Registered project',
                'verbose_name_plural': 'Registered projects',
            },
        ),
        migrations.CreateModel(
            name='StationAction',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('station_action_name', models.CharField(
                    max_length=50,
                    null=True,
                    blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='StationDoc',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('document_title', models.CharField(
                    max_length=40,
                    verbose_name='titre document')),
                ('inscription_date', models.DateField(
                    null=True,
                    verbose_name='date inscription (aaaa-mm-jj)',
                    blank=True)),
                ('document_station', models.FileField(
                    upload_to=gissmo.models.stationdoc_file_name,
                    storage=django.core.files.storage.FileSystemStorage(
                        location=b'/home/olivier/gissmo/upload'),
                    verbose_name='document',
                    blank=True)),
                ('private_link', models.URLField(
                    null=True,
                    verbose_name='lien document prive',
                    blank=True)),
                ('begin_effective', models.DateField(
                    null=True,
                    verbose_name='debut effectivite (aaaa-mm-jj)',
                    blank=True)),
                ('end_effective', models.DateField(
                    null=True,
                    verbose_name='fin effectivite (aaaa-mm-jj)',
                    blank=True)),
            ],
            options={
                'verbose_name': 'Document concernant le site',
                'verbose_name_plural': 'G1. Documents concernants le site',
            },
        ),
        migrations.CreateModel(
            name='StationDocType',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('stationdoc_type_name', models.CharField(
                    max_length=40,
                    verbose_name='type de document')),
            ],
            options={
                'verbose_name_plural': 'S1. Types of document (station)',
            },
        ),
        migrations.CreateModel(
            name='StationSite',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('site_type', models.IntegerField(
                    default=1,
                    verbose_name='type de site',
                    choices=[
                        (1, b'Station sismologique'),
                        (6, b'Site de test'),
                        (7, b'Site th\xc3\xa9orique'),
                        (2, b'Observatoire'),
                        (3, b'Lieu de service apr\xc3\xa8s vente'),
                        (4, b'Lieu ind\xc3\xa9termin\xc3\xa9'),
                        (5, b'Autre')])),
                ('station_code', models.CharField(
                    unique=True,
                    max_length=40,
                    verbose_name='code')),
                ('site_name', models.CharField(
                    max_length=50,
                    null=True,
                    verbose_name='nom site',
                    blank=True)),
                ('latitude', models.DecimalField(
                    null=True,
                    verbose_name='latitude (degre decimal)',
                    max_digits=8,
                    decimal_places=6,
                    blank=True)),
                ('longitude', models.DecimalField(
                    null=True,
                    verbose_name='longitude (degre decimal)',
                    max_digits=9,
                    decimal_places=6,
                    blank=True)),
                ('elevation', models.DecimalField(
                    null=True,
                    verbose_name='elevation (m)',
                    max_digits=5,
                    decimal_places=1,
                    blank=True)),
                ('address', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='adresse',
                    blank=True)),
                ('town', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='commune',
                    blank=True)),
                ('county', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='departement',
                    blank=True)),
                ('region', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='region',
                    blank=True)),
                ('country', models.CharField(
                    max_length=50,
                    null=True,
                    verbose_name='pays',
                    blank=True)),
                ('zip_code', models.CharField(
                    max_length=15,
                    null=True,
                    verbose_name='code postal',
                    blank=True)),
                ('contact', models.TextField(
                    null=True,
                    verbose_name='contact',
                    blank=True)),
                ('note', models.TextField(
                    null=True,
                    verbose_name='note',
                    blank=True)),
                ('private_link', models.URLField(
                    null=True,
                    verbose_name='lien outil interne',
                    blank=True)),
                ('geology', models.CharField(
                    max_length=50,
                    null=True,
                    verbose_name='formation geologique',
                    blank=True)),
                ('restricted_status', models.IntegerField(
                    blank=True,
                    null=True,
                    verbose_name='etat restrictif',
                    choices=[
                        (1, b'Ouvert'),
                        (2, b'Ferme'),
                        (3, b'Partiel')])),
                ('alternate_code', models.CharField(
                    max_length=5,
                    null=True,
                    verbose_name='code alternatif',
                    blank=True)),
                ('historical_code', models.CharField(
                    max_length=5,
                    null=True,
                    verbose_name='code historique',
                    blank=True)),
                ('station_description', models.TextField(
                    null=True,
                    verbose_name='description station',
                    blank=True)),
                ('site_description', models.TextField(
                    null=True,
                    verbose_name='description site',
                    blank=True)),
                ('latitude_unit', models.CharField(
                    default=b'DEGREES',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('latitude_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('latitude_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('latitude_datum', models.CharField(
                    default=b'WSG84',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('longitude_unit', models.CharField(
                    default=b'DEGREES',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('longitude_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('longitude_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('longitude_datum', models.CharField(
                    default=b'WSG84',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('elevation_unit', models.CharField(
                    default=b'METERS',
                    max_length=15,
                    null=True,
                    blank=True)),
                ('elevation_pluserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('elevation_minuserror', models.FloatField(
                    null=True,
                    blank=True)),
                ('operator', models.ForeignKey(
                    verbose_name='operateur',
                    to='gissmo.Actor')),
                ('station_parent', models.ForeignKey(
                    verbose_name='site referent',
                    blank=True,
                    to='gissmo.StationSite',
                    null=True)),
            ],
            options={
                'ordering': ['station_code'],
                'verbose_name': 'site',
                'verbose_name_plural': 'A1. Sites',
            },
        ),
        migrations.CreateModel(
            name='StationState',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('station_state_name', models.CharField(
                    max_length=50,
                    null=True,
                    blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='stationdoc',
            name='document_type',
            field=models.ForeignKey(
                verbose_name='type de document',
                blank=True,
                to='gissmo.StationDocType',
                null=True),
        ),
        migrations.AddField(
            model_name='stationdoc',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stationdoc',
            name='station',
            field=models.ForeignKey(
                verbose_name='site',
                to='gissmo.StationSite'),
        ),
        migrations.AddField(
            model_name='project',
            name='station',
            field=models.ManyToManyField(
                to='gissmo.StationSite',
                blank=True),
        ),
        migrations.AddField(
            model_name='intervequip',
            name='station',
            field=models.ForeignKey(
                verbose_name='site',
                blank=True,
                to='gissmo.StationSite',
                null=True),
        ),
        migrations.AddField(
            model_name='intervention',
            name='station',
            field=models.ForeignKey(
                verbose_name='site',
                to='gissmo.StationSite'),
        ),
        migrations.AddField(
            model_name='intervactor',
            name='intervention',
            field=models.ForeignKey(
                verbose_name='intervention',
                to='gissmo.Intervention'),
        ),
        migrations.AddField(
            model_name='equipmodeldoc',
            name='document_type',
            field=models.ForeignKey(
                verbose_name='type de document',
                blank=True,
                to='gissmo.EquipModelDocType',
                null=True),
        ),
        migrations.AddField(
            model_name='equipmodeldoc',
            name='equip_model',
            field=smart_selects.db_fields.ChainedForeignKey(
                auto_choose=True,
                to='gissmo.EquipModel',
                chained_model_field=b'equip_type',
                chained_field=b'equip_type',
                verbose_name="modele d'equipement"),
        ),
        migrations.AddField(
            model_name='equipmodeldoc',
            name='equip_supertype',
            field=models.ForeignKey(
                verbose_name="supertype d'equipement",
                to='gissmo.EquipSupertype'),
        ),
        migrations.AddField(
            model_name='equipmodeldoc',
            name='equip_type',
            field=smart_selects.db_fields.ChainedForeignKey(
                auto_choose=True,
                to='gissmo.EquipType',
                chained_model_field=b'equip_supertype',
                chained_field=b'equip_supertype',
                verbose_name="type d'equipement"),
        ),
        migrations.AddField(
            model_name='equipmodeldoc',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='equipmodel',
            name='equip_supertype',
            field=models.ForeignKey(
                verbose_name="supertype d'equipement",
                to='gissmo.EquipSupertype'),
        ),
        migrations.AddField(
            model_name='equipmodel',
            name='equip_type',
            field=smart_selects.db_fields.ChainedForeignKey(
                auto_choose=True,
                to='gissmo.EquipType',
                chained_model_field=b'equip_supertype',
                chained_field=b'equip_supertype',
                verbose_name="type d'equipement"),
        ),
        migrations.AddField(
            model_name='equipment',
            name='equip_model',
            field=smart_selects.db_fields.ChainedForeignKey(
                auto_choose=True,
                to='gissmo.EquipModel',
                chained_model_field=b'equip_type',
                chained_field=b'equip_type',
                verbose_name="modele d'equipement"),
        ),
        migrations.AddField(
            model_name='equipment',
            name='equip_supertype',
            field=models.ForeignKey(
                verbose_name="supertype d'equipement",
                to='gissmo.EquipSupertype'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='equip_type',
            field=smart_selects.db_fields.ChainedForeignKey(
                auto_choose=True, to='gissmo.EquipType',
                chained_model_field=b'equip_supertype',
                chained_field=b'equip_supertype',
                verbose_name="type d'equipement"),
        ),
        migrations.AddField(
            model_name='equipment',
            name='owner',
            field=models.ForeignKey(
                verbose_name='proprietaire',
                to='gissmo.Actor'),
        ),
        migrations.AddField(
            model_name='equipdoc',
            name='document_type',
            field=models.ForeignKey(
                verbose_name='type de document',
                blank=True,
                to='gissmo.EquipDocType',
                null=True),
        ),
        migrations.AddField(
            model_name='equipdoc',
            name='equip',
            field=smart_selects.db_fields.ChainedForeignKey(
                auto_choose=True,
                to='gissmo.Equipment',
                chained_model_field=b'equip_model',
                chained_field=b'equip_model',
                verbose_name='equipement'),
        ),
        migrations.AddField(
            model_name='equipdoc',
            name='equip_model',
            field=smart_selects.db_fields.ChainedForeignKey(
                auto_choose=True,
                to='gissmo.EquipModel',
                chained_model_field=b'equip_type',
                chained_field=b'equip_type',
                verbose_name="modele d'equipement"),
        ),
        migrations.AddField(
            model_name='equipdoc',
            name='equip_supertype',
            field=models.ForeignKey(
                verbose_name="supertype d'equipement",
                to='gissmo.EquipSupertype'),
        ),
        migrations.AddField(
            model_name='equipdoc',
            name='equip_type',
            field=smart_selects.db_fields.ChainedForeignKey(
                auto_choose=True,
                to='gissmo.EquipType',
                chained_model_field=b'equip_supertype',
                chained_field=b'equip_supertype',
                verbose_name="type d'equipement"),
        ),
        migrations.AddField(
            model_name='equipdoc',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentstationsite',
            name='station',
            field=models.ForeignKey(
                verbose_name='site',
                to='gissmo.StationSite'),
        ),
        migrations.AddField(
            model_name='commentnetwork',
            name='network',
            field=models.ForeignKey(
                verbose_name='reseau',
                to='gissmo.Network'),
        ),
        migrations.AddField(
            model_name='channel',
            name='channel_code',
            field=models.ForeignKey(
                verbose_name='code du canal',
                to='gissmo.ChannelCode'),
        ),
        migrations.AddField(
            model_name='channel',
            name='data_type',
            field=models.ManyToManyField(
                to='gissmo.DataType',
                verbose_name='donnees produites',
                blank=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='network',
            field=models.ForeignKey(
                verbose_name='code reseau',
                to='gissmo.Network'),
        ),
        migrations.AddField(
            model_name='channel',
            name='station',
            field=models.ForeignKey(
                verbose_name='station',
                to='gissmo.StationSite'),
        ),
        migrations.AddField(
            model_name='chainconfig',
            name='channel',
            field=models.ForeignKey(
                verbose_name='canal',
                to='gissmo.Channel'),
        ),
        migrations.AddField(
            model_name='chainconfig',
            name='parameter',
            field=models.ForeignKey(
                verbose_name='parametre',
                to='gissmo.ParameterEquip'),
        ),
        migrations.AddField(
            model_name='chainconfig',
            name='value',
            field=models.ForeignKey(
                verbose_name='value',
                to='gissmo.ParameterValue'),
        ),
        migrations.AddField(
            model_name='chain',
            name='channel',
            field=models.ForeignKey(
                verbose_name='canal',
                to='gissmo.Channel'),
        ),
        migrations.AddField(
            model_name='chain',
            name='equip',
            field=models.ForeignKey(
                verbose_name='equipement',
                to='gissmo.Equipment'),
        ),
        migrations.AddField(
            model_name='built',
            name='built_type',
            field=models.ForeignKey(
                verbose_name='type de bati',
                to='gissmo.BuiltType'),
        ),
        migrations.AddField(
            model_name='built',
            name='station',
            field=models.ForeignKey(
                verbose_name='site',
                to='gissmo.StationSite'),
        ),
        migrations.AlterUniqueTogether(
            name='stationdoc',
            unique_together=set([
                ('station', 'document_title', 'inscription_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='parametervalue',
            unique_together=set([('parameter', 'value')]),
        ),
        migrations.AlterUniqueTogether(
            name='parameterequip',
            unique_together=set([('equip_model', 'parameter_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='intervention',
            unique_together=set([('station', 'intervention_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='equipmodeldoc',
            unique_together=set([
                ('equip_model', 'document_title', 'inscription_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='equipment',
            unique_together=set([(
                'equip_supertype',
                'equip_type',
                'equip_model',
                'serial_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='equipdoc',
            unique_together=set([
                ('equip', 'document_title', 'inscription_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='channel',
            unique_together=set([(
                'station',
                'network',
                'channel_code',
                'location_code',
                'start_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='chainconfig',
            unique_together=set([('channel', 'chain', 'parameter')]),
        ),
        migrations.AlterUniqueTogether(
            name='chain',
            unique_together=set([('channel', 'order')]),
        ),
        migrations.AlterUniqueTogether(
            name='built',
            unique_together=set([
                ('station', 'built_type', 'built_short_desc')]),
        ),
    ]
