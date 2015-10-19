# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields
import gissmo.models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0004_auto_20151016_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actor',
            name='actor_type',
            field=models.IntegerField(default=7, verbose_name="Type d'intervenant", choices=[(1, 'Observatoire/Laboratoire'), (2, 'Ingénieur/Technicien'), (3, 'Réseau'), (4, 'Entreprise'), (5, 'Entreprise SAV'), (6, 'Inconnu'), (7, 'Autre')]),
        ),
        migrations.AlterField(
            model_name='chain',
            name='order',
            field=models.IntegerField(verbose_name='Type', choices=[(1, 'Sensor'), (2, 'PreAmplifier'), (3, 'DataLogger'), (4, 'Equipment'), (5, 'Other_1'), (6, 'Other_2'), (7, 'Other_3'), (7, 'Other_4'), (9, 'Other_5')]),
        ),
        migrations.AlterField(
            model_name='channel',
            name='azimuth_unit',
            field=models.CharField(blank=True, default='DEGREES', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='clock_drift_unit',
            field=models.CharField(blank=True, default='SECONDS/SAMPLE', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='depth_unit',
            field=models.CharField(blank=True, default='METERS', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='dip_unit',
            field=models.CharField(blank=True, default='DEGREES', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='elevation_unit',
            field=models.CharField(blank=True, default='METERS', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='latitude_datum',
            field=models.CharField(blank=True, default='WSG84', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='latitude_unit',
            field=models.CharField(blank=True, default='DEGREES', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='longitude_datum',
            field=models.CharField(blank=True, default='WSG84', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='longitude_unit',
            field=models.CharField(blank=True, default='DEGREES', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='restricted_status',
            field=models.IntegerField(blank=True, verbose_name='etat restrictif', choices=[(1, 'Ouvert'), (2, 'Ferme'), (3, 'Partiel')], null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='sample_rate_unit',
            field=models.CharField(blank=True, default='SAMPLES/S', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='document_equip',
            field=models.FileField(blank=True, verbose_name='document', upload_to=gissmo.models.equipdoc_file_name, storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/upload')),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='equip',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, verbose_name='equipement', to='gissmo.Equipment', chained_field='equip_model', chained_model_field='equip_model'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='equip_model',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, verbose_name="modele d'equipement", to='gissmo.EquipModel', chained_field='equip_type', chained_model_field='equip_type'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='equip_type',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, verbose_name="type d'equipement", to='gissmo.EquipType', chained_field='equip_supertype', chained_model_field='equip_supertype'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equip_model',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, verbose_name="modele d'equipement", to='gissmo.EquipModel', chained_field='equip_type', chained_model_field='equip_type'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equip_type',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, verbose_name="type d'equipement", to='gissmo.EquipType', chained_field='equip_supertype', chained_model_field='equip_supertype'),
        ),
        migrations.AlterField(
            model_name='equipmodel',
            name='equip_type',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, verbose_name="type d'equipement", to='gissmo.EquipType', chained_field='equip_supertype', chained_model_field='equip_supertype'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='document_equip_model',
            field=models.FileField(blank=True, verbose_name='document', upload_to=gissmo.models.equipmodeldoc_file_name, storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/upload')),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='equip_model',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, verbose_name="modele d'equipement", to='gissmo.EquipModel', chained_field='equip_type', chained_model_field='equip_type'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='equip_type',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, verbose_name="type d'equipement", to='gissmo.EquipType', chained_field='equip_supertype', chained_model_field='equip_supertype'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip_action',
            field=models.IntegerField(verbose_name='action', choices=[(1, 'Acheter'), (2, 'Tester'), (3, 'Installer'), (4, 'Désinstaller'), (5, 'Constater défaut'), (6, 'Effectuer maintenance préventive à distance'), (7, 'Effectuer maintenance corrective à distance'), (8, 'Effectuer maintenance préventive sur site'), (9, 'Effectuer maintenance corrective sur site'), (10, 'Expédier'), (11, 'Recevoir'), (12, 'Mettre hors usage'), (13, 'Constater disparition'), (14, 'Retrouver suite à une disparition'), (15, 'Mettre au rebut'), (16, 'Autre')]),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip_state',
            field=models.IntegerField(verbose_name='etat', choices=[(1, 'En opération'), (2, 'A tester'), (3, 'Disponible'), (4, 'En défaillance'), (5, 'En panne'), (6, 'En transit'), (7, "Hors d'usage"), (8, 'Disparu'), (9, 'Au rebut'), (10, 'Autre')]),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='station_action',
            field=models.IntegerField(verbose_name='action', choices=[(1, 'Créer code station'), (2, 'Installer station'), (11, 'Débuter test'), (12, 'Terminer test'), (3, 'Mettre en opération'), (4, 'Constater défaillance'), (5, 'Effectuer maintenance préventive à distance'), (6, 'Effectuer maintenance corrective à distance'), (7, 'Effectuer maintenance préventive sur site'), (8, 'Effectuer maintenance corrective sur site'), (9, 'Démanteler'), (10, 'Autre')]),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='station_state',
            field=models.IntegerField(blank=True, verbose_name='etat', choices=[(1, 'En installation'), (7, 'En test'), (2, 'En opération'), (3, 'En défaillance'), (4, 'En panne'), (5, 'Fermée'), (6, 'Autre')], null=True),
        ),
        migrations.AlterField(
            model_name='network',
            name='restricted_status',
            field=models.IntegerField(blank=True, verbose_name='etat restrictif', choices=[(1, 'Ouvert'), (2, 'Ferme'), (3, 'Partiel')], null=True),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='document_station',
            field=models.FileField(blank=True, verbose_name='document', upload_to=gissmo.models.stationdoc_file_name, storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/upload')),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='elevation_unit',
            field=models.CharField(blank=True, default='METERS', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='latitude_datum',
            field=models.CharField(blank=True, default='WSG84', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='latitude_unit',
            field=models.CharField(blank=True, default='DEGREES', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='longitude_datum',
            field=models.CharField(blank=True, default='WSG84', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='longitude_unit',
            field=models.CharField(blank=True, default='DEGREES', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='restricted_status',
            field=models.IntegerField(blank=True, verbose_name='etat restrictif', choices=[(1, 'Ouvert'), (2, 'Ferme'), (3, 'Partiel')], null=True),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='site_type',
            field=models.IntegerField(default=1, verbose_name='type de site', choices=[(1, 'Station sismologique'), (6, 'Site de test'), (7, 'Site théorique'), (2, 'Observatoire'), (3, 'Lieu de service après vente'), (4, 'Lieu indéterminé'), (5, 'Autre')]),
        ),
    ]
