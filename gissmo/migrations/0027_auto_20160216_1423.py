# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import gissmo.models
import gissmo.validators
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0026_auto_20160126_1534'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actor',
            options={'ordering': ['actor_name'], 'verbose_name': 'Actor'},
        ),
        migrations.AlterModelOptions(
            name='built',
            options={'verbose_name': 'Place'},
        ),
        migrations.AlterModelOptions(
            name='builttype',
            options={'ordering': ['built_type_name'], 'verbose_name': 'Place type'},
        ),
        migrations.AlterModelOptions(
            name='calibrationunit',
            options={'verbose_name': 'Unit type'},
        ),
        migrations.AlterModelOptions(
            name='chain',
            options={'verbose_name': 'Acquisition chain'},
        ),
        migrations.AlterModelOptions(
            name='chainconfig',
            options={'verbose_name': 'Configuration'},
        ),
        migrations.AlterModelOptions(
            name='channel',
            options={'verbose_name': 'Channel'},
        ),
        migrations.AlterModelOptions(
            name='channelcode',
            options={'verbose_name': 'Channel code'},
        ),
        migrations.AlterModelOptions(
            name='datatype',
            options={'verbose_name': 'Data type'},
        ),
        migrations.AlterModelOptions(
            name='equipdoc',
            options={'verbose_name': 'Document (equip.)', 'verbose_name_plural': 'Documents (equip.)'},
        ),
        migrations.AlterModelOptions(
            name='equipdoctype',
            options={'verbose_name': 'Document type (equip.)', 'verbose_name_plural': 'Document types (equip.)'},
        ),
        migrations.AlterModelOptions(
            name='equipment',
            options={'verbose_name': 'Equipment'},
        ),
        migrations.AlterModelOptions(
            name='equipmodel',
            options={'ordering': ['equip_model_name'], 'verbose_name': 'Equipment model'},
        ),
        migrations.AlterModelOptions(
            name='equipmodeldoc',
            options={'verbose_name': "Document (equip.'s model)", 'verbose_name_plural': "Documents (equip.'s model)"},
        ),
        migrations.AlterModelOptions(
            name='equipmodeldoctype',
            options={'verbose_name': 'Document type (equip. model)', 'verbose_name_plural': 'Document types (equip. model)'},
        ),
        migrations.AlterModelOptions(
            name='equipsupertype',
            options={'ordering': ['equip_supertype_name'], 'verbose_name': 'Equipment Supertype'},
        ),
        migrations.AlterModelOptions(
            name='equiptype',
            options={'ordering': ['equip_type_name'], 'verbose_name': 'Equipment type'},
        ),
        migrations.AlterModelOptions(
            name='forbiddenequipmentmodel',
            options={'verbose_name': "Forbidden Equipment's model"},
        ),
        migrations.AlterModelOptions(
            name='intervactor',
            options={'verbose_name': 'Operator'},
        ),
        migrations.AlterModelOptions(
            name='intervention',
            options={'verbose_name': 'Intervention'},
        ),
        migrations.AlterModelOptions(
            name='intervequip',
            options={'verbose_name': 'Equipment intervention'},
        ),
        migrations.AlterModelOptions(
            name='intervstation',
            options={'verbose_name': 'Site intervention'},
        ),
        migrations.AlterModelOptions(
            name='loggedactions',
            options={'managed': False, 'verbose_name': 'Logged action'},
        ),
        migrations.AlterModelOptions(
            name='network',
            options={'verbose_name': 'Network'},
        ),
        migrations.AlterModelOptions(
            name='parameterequip',
            options={'verbose_name': "Equipment's parameter"},
        ),
        migrations.AlterModelOptions(
            name='parametervalue',
            options={'verbose_name': "Parameter's value"},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'verbose_name': 'Project'},
        ),
        migrations.AlterModelOptions(
            name='projectuser',
            options={'verbose_name': "User's project"},
        ),
        migrations.AlterModelOptions(
            name='stationdoc',
            options={'verbose_name': 'Document (site)', 'verbose_name_plural': 'Documents (site)'},
        ),
        migrations.AlterModelOptions(
            name='stationdoctype',
            options={'verbose_name': 'Document type (site)', 'verbose_name_plural': 'Document types (site)'},
        ),
        migrations.AlterModelOptions(
            name='stationsite',
            options={'ordering': ['station_code'], 'verbose_name': 'Site'},
        ),
        migrations.RemoveField(
            model_name='network',
            name='code',
        ),
        migrations.AlterField(
            model_name='actor',
            name='actor_name',
            field=models.CharField(unique=True, max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='actor',
            name='actor_note',
            field=models.TextField(null=True, blank=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='actor',
            name='actor_parent',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.Actor', verbose_name='Membership group'),
        ),
        migrations.AlterField(
            model_name='actor',
            name='actor_type',
            field=models.IntegerField(default=7, choices=[(1, 'Observatory/Laboratory'), (2, 'Engineer/Technician'), (3, 'Network'), (4, 'Business'), (5, 'Customer service Company'), (6, 'Unknown'), (7, 'Other')], verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='built',
            name='built_note',
            field=models.TextField(null=True, blank=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='built',
            name='built_short_desc',
            field=models.CharField(max_length=40, verbose_name='Short description', default='Unknown'),
        ),
        migrations.AlterField(
            model_name='built',
            name='built_type',
            field=models.ForeignKey(to='gissmo.BuiltType', verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='built',
            name='station',
            field=models.ForeignKey(to='gissmo.StationSite', verbose_name='Site'),
        ),
        migrations.AlterField(
            model_name='builttype',
            name='built_type_name',
            field=models.CharField(max_length=40, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='calibrationunit',
            name='description',
            field=models.TextField(null=True, blank=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='calibrationunit',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='chain',
            name='channel',
            field=models.ForeignKey(to='gissmo.Channel', verbose_name='Channel'),
        ),
        migrations.AlterField(
            model_name='chain',
            name='equip',
            field=models.ForeignKey(to='gissmo.Equipment', verbose_name='Equipment'),
        ),
        migrations.AlterField(
            model_name='chainconfig',
            name='chain',
            field=models.ForeignKey(to='gissmo.Chain', verbose_name='Acquisition chain'),
        ),
        migrations.AlterField(
            model_name='chainconfig',
            name='channel',
            field=models.ForeignKey(to='gissmo.Channel', verbose_name='Channel'),
        ),
        migrations.AlterField(
            model_name='chainconfig',
            name='parameter',
            field=models.ForeignKey(to='gissmo.ParameterEquip', verbose_name='Parameter'),
        ),
        migrations.AlterField(
            model_name='chainconfig',
            name='value',
            field=models.ForeignKey(to='gissmo.ParameterValue', verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='alternate_code',
            field=models.CharField(null=True, max_length=5, blank=True, verbose_name='Alternate code'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='azimuth',
            field=models.DecimalField(max_digits=4, verbose_name='Azimut (°)', decimal_places=1),
        ),
        migrations.AlterField(
            model_name='channel',
            name='calibration_units',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.CalibrationUnit', verbose_name='Calibration unit'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='channel_code',
            field=models.ForeignKey(to='gissmo.ChannelCode', verbose_name='Channel code'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='clock_drift',
            field=models.FloatField(null=True, blank=True, verbose_name='Clock drift (seconds/sample)'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='data_type',
            field=models.ManyToManyField(blank=True, verbose_name='Data types', to='gissmo.DataType'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='depth',
            field=models.DecimalField(max_digits=4, verbose_name='Depth (m)', decimal_places=1),
        ),
        migrations.AlterField(
            model_name='channel',
            name='description',
            field=models.TextField(null=True, blank=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='dip',
            field=models.DecimalField(max_digits=3, verbose_name='Dip (°)', decimal_places=1),
        ),
        migrations.AlterField(
            model_name='channel',
            name='elevation',
            field=models.DecimalField(max_digits=5, verbose_name='Elevation (m)', decimal_places=1),
        ),
        migrations.AlterField(
            model_name='channel',
            name='end_date',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Ending date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='historical_code',
            field=models.CharField(null=True, max_length=5, blank=True, verbose_name='Historical code'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='latitude',
            field=models.DecimalField(max_digits=8, verbose_name='Latitude (°)', decimal_places=6),
        ),
        migrations.AlterField(
            model_name='channel',
            name='location_code',
            field=models.CharField(null=True, max_length=2, blank=True, verbose_name='Location code'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='longitude',
            field=models.DecimalField(max_digits=9, verbose_name='Longitude (°)', decimal_places=6),
        ),
        migrations.AlterField(
            model_name='channel',
            name='network',
            field=models.ForeignKey(to='gissmo.Network', verbose_name='Network'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='restricted_status',
            field=models.IntegerField(null=True, choices=[(1, 'Open'), (2, 'Closed'), (3, 'Partial')], blank=True, verbose_name='Restrictive status'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='sample_rate',
            field=models.FloatField(verbose_name='Sample rate (Hz)'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='start_date',
            field=models.DateTimeField(verbose_name='Starting date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='station',
            field=models.ForeignKey(to='gissmo.StationSite', verbose_name='Station'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='storage_format',
            field=models.CharField(null=True, max_length=50, blank=True, verbose_name='Storage format'),
        ),
        migrations.AlterField(
            model_name='channelcode',
            name='channel_code',
            field=models.CharField(serialize=False, max_length=3, verbose_name='Code', primary_key=True),
        ),
        migrations.AlterField(
            model_name='channelcode',
            name='validation_rule',
            field=models.TextField(null=True, blank=True, verbose_name='Validation rule'),
        ),
        migrations.AlterField(
            model_name='datatype',
            name='type_description',
            field=models.CharField(max_length=50, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='begin_effective',
            field=models.DateField(null=True, blank=True, verbose_name='Start date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='document_equip',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/project/gissmo/upload'), blank=True, verbose_name='Document', upload_to=gissmo.models.equipdoc_file_name),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='document_title',
            field=models.CharField(max_length=40, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='document_type',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.EquipDocType', verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='end_effective',
            field=models.DateField(null=True, blank=True, verbose_name='End date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='equip',
            field=models.ForeignKey(to='gissmo.Equipment', verbose_name='Equipment'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='inscription_date',
            field=models.DateField(null=True, blank=True, verbose_name='Registration date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='equipdoc',
            name='private_link',
            field=models.URLField(null=True, blank=True, verbose_name='Private document link'),
        ),
        migrations.AlterField(
            model_name='equipdoctype',
            name='equipdoc_type_name',
            field=models.CharField(max_length=40, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='contact',
            field=models.TextField(null=True, blank=True, verbose_name='Contact'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equip_model',
            field=models.ForeignKey(validators=[gissmo.validators.validate_equip_model], to='gissmo.EquipModel', verbose_name='Model'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='last_state',
            field=models.IntegerField(null=True, choices=[(1, 'Operation in progress'), (2, 'To be tested'), (3, 'Available'), (4, 'Failure'), (5, 'Breakdown'), (6, 'Transit in progress'), (7, 'Out of use'), (8, 'Lost'), (9, 'Waste'), (10, 'Other')], blank=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='last_station',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.StationSite', verbose_name='Last place'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='note',
            field=models.TextField(null=True, blank=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='owner',
            field=models.ForeignKey(to='gissmo.Actor', verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='purchase_date',
            field=models.DateField(null=True, blank=True, verbose_name='Purchase date'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='serial_number',
            field=models.CharField(max_length=50, verbose_name='Serial number'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='vendor',
            field=models.CharField(null=True, max_length=50, blank=True, verbose_name='Seller'),
        ),
        migrations.AlterField(
            model_name='equipmodel',
            name='equip_model_name',
            field=models.CharField(max_length=50, verbose_name='Model'),
        ),
        migrations.AlterField(
            model_name='equipmodel',
            name='equip_type',
            field=models.ForeignKey(to='gissmo.EquipType', verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='equipmodel',
            name='is_network_model',
            field=models.BooleanField(default=False, verbose_name='Network configurable?'),
        ),
        migrations.AlterField(
            model_name='equipmodel',
            name='manufacturer',
            field=models.CharField(max_length=50, verbose_name='Manufacturer', default='Unknown'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='begin_effective',
            field=models.DateField(null=True, blank=True, verbose_name='Start date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='document_equip_model',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/project/gissmo/upload'), blank=True, verbose_name='Document', upload_to=gissmo.models.equipmodeldoc_file_name),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='document_title',
            field=models.CharField(max_length=40, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='document_type',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.EquipModelDocType', verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='end_effective',
            field=models.DateField(null=True, blank=True, verbose_name='End date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='equip_model',
            field=models.ForeignKey(to='gissmo.EquipModel', verbose_name='Equipment model'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='inscription_date',
            field=models.DateField(null=True, blank=True, verbose_name='Registration date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoc',
            name='private_link',
            field=models.URLField(null=True, blank=True, verbose_name='Private document link'),
        ),
        migrations.AlterField(
            model_name='equipmodeldoctype',
            name='equipmodeldoc_type_name',
            field=models.CharField(max_length=40, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='equipsupertype',
            name='equip_supertype_name',
            field=models.CharField(max_length=40, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='equiptype',
            name='equip_supertype',
            field=models.ForeignKey(to='gissmo.EquipSupertype', verbose_name='Supertype'),
        ),
        migrations.AlterField(
            model_name='equiptype',
            name='equip_type_name',
            field=models.CharField(max_length=40, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='intervactor',
            name='actor',
            field=models.ForeignKey(to='gissmo.Actor', verbose_name='Operator'),
        ),
        migrations.AlterField(
            model_name='intervactor',
            name='intervention',
            field=models.ForeignKey(to='gissmo.Intervention', verbose_name='Intervention'),
        ),
        migrations.AlterField(
            model_name='intervactor',
            name='note',
            field=models.TextField(null=True, blank=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='intervention_date',
            field=models.DateTimeField(verbose_name='Date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='note',
            field=models.TextField(null=True, blank=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='intervention',
            name='station',
            field=models.ForeignKey(to='gissmo.StationSite', verbose_name='Site'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='built',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.Built', verbose_name='Place'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip',
            field=models.ForeignKey(to='gissmo.Equipment', verbose_name='Equipment'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip_action',
            field=models.IntegerField(choices=[(1, 'Buy'), (2, 'Test'), (3, 'Install'), (4, 'Uninstall'), (5, 'Observe failure'), (6, 'Perform remote preventive maintenance'), (7, 'Perform remote corrective maintenance'), (8, 'Perform preventive maintenance locally'), (9, 'Perform corrective maintenance locally'), (10, 'Send'), (11, 'Receive'), (12, 'Put is as out of use'), (13, 'Observe that equipment is lost'), (14, 'Find it after being lost'), (15, 'Put it as waste'), (16, 'Other')], verbose_name='Action'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='equip_state',
            field=models.IntegerField(choices=[(1, 'Operation in progress'), (2, 'To be tested'), (3, 'Available'), (4, 'Failure'), (5, 'Breakdown'), (6, 'Transit in progress'), (7, 'Out of use'), (8, 'Lost'), (9, 'Waste'), (10, 'Other')], verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='intervention',
            field=models.ForeignKey(to='gissmo.Intervention', verbose_name='Intervention'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='note',
            field=models.TextField(null=True, blank=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='intervequip',
            name='station',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.StationSite', verbose_name='Site'),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='intervention',
            field=models.ForeignKey(to='gissmo.Intervention', verbose_name='Intervention'),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='note',
            field=models.TextField(null=True, blank=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='station_action',
            field=models.IntegerField(choices=[(1, 'Create station code'), (2, 'Install station'), (11, 'Start test'), (12, 'Finish test'), (3, 'Run'), (4, 'Observe failure'), (5, 'Perform REMOTE PREVentive maintenance'), (6, 'Perform REMOTE CORrective maintenance'), (7, 'Perform LOCAL PREVentive maintenance'), (8, 'Perform LOCAL CORrective maintenance'), (9, 'Shut down'), (10, 'Other')], verbose_name='Action'),
        ),
        migrations.AlterField(
            model_name='intervstation',
            name='station_state',
            field=models.IntegerField(null=True, choices=[(1, 'Installing'), (7, 'Testing'), (2, 'Running'), (3, 'Broken'), (4, 'Failure'), (5, 'Closed'), (6, 'Other')], blank=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='network',
            name='alternate_code',
            field=models.CharField(null=True, max_length=5, blank=True, verbose_name='Alternate code'),
        ),
        migrations.AlterField(
            model_name='network',
            name='description',
            field=models.TextField(null=True, blank=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='network',
            name='end_date',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Ending date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='network',
            name='historical_code',
            field=models.CharField(null=True, max_length=5, blank=True, verbose_name='Historical code'),
        ),
        migrations.AlterField(
            model_name='network',
            name='network_code',
            field=models.CharField(max_length=5, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='network',
            name='network_name',
            field=models.CharField(null=True, max_length=50, blank=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='network',
            name='restricted_status',
            field=models.IntegerField(null=True, choices=[(1, 'Open'), (2, 'Closed'), (3, 'Partial')], blank=True, verbose_name='Restricted status'),
        ),
        migrations.AlterField(
            model_name='network',
            name='start_date',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Starting date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='parameterequip',
            name='equip_model',
            field=models.ForeignKey(to='gissmo.EquipModel', verbose_name='Equipment model'),
        ),
        migrations.AlterField(
            model_name='parameterequip',
            name='parameter_name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='default_value',
            field=models.BooleanField(default=None, verbose_name='Default value'),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='parameter',
            field=models.ForeignKey(to='gissmo.ParameterEquip', verbose_name='Parameter'),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='value',
            field=models.CharField(max_length=50, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='station',
            field=models.ManyToManyField(blank=True, verbose_name='Site', to='gissmo.StationSite'),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='begin_effective',
            field=models.DateField(null=True, blank=True, verbose_name='Start date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='document_station',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/home/olivier/gissmo/project/gissmo/upload'), blank=True, verbose_name='Document', upload_to=gissmo.models.stationdoc_file_name),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='document_title',
            field=models.CharField(max_length=40, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='document_type',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.StationDocType', verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='end_effective',
            field=models.DateField(null=True, blank=True, verbose_name='End date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='inscription_date',
            field=models.DateField(null=True, blank=True, verbose_name='Registration date (yyyy-mm-dd)'),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='private_link',
            field=models.URLField(null=True, blank=True, verbose_name='Private document link'),
        ),
        migrations.AlterField(
            model_name='stationdoc',
            name='station',
            field=models.ForeignKey(to='gissmo.StationSite', verbose_name='Site'),
        ),
        migrations.AlterField(
            model_name='stationdoctype',
            name='stationdoc_type_name',
            field=models.CharField(max_length=40, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='address',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='alternate_code',
            field=models.CharField(null=True, max_length=5, blank=True, verbose_name='Alternate code'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='contact',
            field=models.TextField(null=True, blank=True, verbose_name='Contact'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='country',
            field=models.CharField(null=True, max_length=50, blank=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='county',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='District'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='creation_date',
            field=models.DateField(null=True, blank=True, verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='elevation',
            field=models.DecimalField(null=True, blank=True, verbose_name='Elevation (m)', decimal_places=1, max_digits=5),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='geology',
            field=models.CharField(null=True, max_length=50, blank=True, verbose_name='Geological formation'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='historical_code',
            field=models.CharField(null=True, max_length=5, blank=True, verbose_name='Historical code'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='last_state',
            field=models.IntegerField(null=True, choices=[(1, 'Installing'), (7, 'Testing'), (2, 'Running'), (3, 'Broken'), (4, 'Failure'), (5, 'Closed'), (6, 'Other')], blank=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='latitude',
            field=models.DecimalField(null=True, blank=True, verbose_name='Latitude (°)', decimal_places=6, max_digits=8),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='longitude',
            field=models.DecimalField(null=True, blank=True, verbose_name='Longitude (°)', decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='note',
            field=models.TextField(null=True, blank=True, verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='operator',
            field=models.ForeignKey(to='gissmo.Actor', verbose_name='Operator'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='private_link',
            field=models.URLField(null=True, blank=True, verbose_name='External link'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='region',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='Region'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='restricted_status',
            field=models.IntegerField(null=True, choices=[(1, 'Open'), (2, 'Closed'), (3, 'Partial')], blank=True, verbose_name='Restrictive status'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='site_description',
            field=models.TextField(null=True, blank=True, verbose_name='Site description'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='site_name',
            field=models.CharField(null=True, max_length=50, blank=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='site_type',
            field=models.IntegerField(default=1, choices=[(1, 'Measuring site'), (6, 'Potential site'), (7, 'Theoretical site'), (2, 'Agency'), (3, 'Customer service place'), (4, 'Undefined'), (5, 'Other')], verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='station_code',
            field=models.CharField(unique=True, max_length=40, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='station_description',
            field=models.TextField(null=True, blank=True, verbose_name='Station description'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='station_parent',
            field=models.ForeignKey(null=True, blank=True, to='gissmo.StationSite', verbose_name='Linked site (referent)'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='town',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='stationsite',
            name='zip_code',
            field=models.CharField(null=True, max_length=15, blank=True, verbose_name='Zip code'),
        ),
    ]
