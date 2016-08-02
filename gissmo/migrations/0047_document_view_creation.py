# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gissmo', '0046_auto_20160701_1505'),
    ]

    # ::INTEGER on SQL request avoids this problem:
    # https://www.postgresql.org/message-id/201104122018.p3CKIlWR042915@wwwmaster.postgresql.org
    operations = [
        migrations.RunSQL(
            """
            DROP VIEW IF EXISTS gissmo_documentview;

            CREATE OR REPLACE VIEW gissmo_documentview
            AS
                SELECT row_number()  OVER () AS id,
                    'equipment' AS model,
                    edt.equipdoc_type_name AS type,
                    ed.document_title AS title,
                    ed.begin_effective AS start,
                    ed.end_effective AS end,
                    ed.document_equip AS file,
                    NULL::INTEGER AS station_id,
                    ed.equip_id AS equipment_id,
                    NULL AS equipmodel,
                    NULL::INTEGER AS intervention_id
                FROM gissmo_equipdoc AS ed, gissmo_equipdoctype AS edt
                WHERE ed.document_type_id = edt.id
            UNION
                SELECT row_number() OVER () as id,
                    'station' AS model,
                    sdt.stationdoc_type_name AS type,
                    sd.document_title AS title,
                    sd.begin_effective AS start,
                    sd.end_effective AS end,
                    sd.document_station AS file,
                    sd.station_id AS station_id,
                    NULL AS equipment_id,
                    NULL AS equipmodel,
                    NULL AS intervention_id
                FROM gissmo_stationdoc AS sd, gissmo_stationdoctype AS sdt
                WHERE sd.document_type_id = sdt.id
            UNION
                SELECT row_number() OVER () AS id,
                    'equipment_model' AS model,
                    emt.equipmodeldoc_type_name AS type,
                    em.document_title AS title,
                    em.begin_effective AS start,
                    em.end_effective AS end,
                    em.document_equip_model AS file,
                    NULL AS station_id,
                    NULL AS equipment_id,
                    emo.equip_model_name AS equipmodel,
                    NULL AS intervention_id
                FROM
                    gissmo_equipmodeldoc AS em,
                    gissmo_equipmodeldoctype AS emt,
                    gissmo_equipmodel AS emo
                WHERE em.document_type_id = emt.id
                AND em.equip_model_id = emo.id
            UNION
                SELECT row_number() OVER () AS id,
                    'intervention' AS model,
                    NULL AS type,
                    doc.description AS title,
                    interv.intervention_date AS start,
                    NULL AS end,
                    doc._file AS file,
                    NULL AS station_id,
                    NULL AS equipment_id,
                    NULL AS equipmodel,
                    doc.intervention_id AS intervention_id
                FROM gissmo_intervdoc AS doc, gissmo_intervention AS interv
                WHERE doc.intervention_id = interv.id
            ;
            """
        ),
        migrations.CreateModel(
            name='DocumentView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('model', models.CharField(max_length=30)),
                ('_type', models.IntegerField(null=True)),
                ('title', models.CharField(null=True, max_length=40)),
                ('start', models.DateTimeField(null=True)),
                ('end', models.DateTimeField(null=True)),
                ('_file', models.FileField(upload_to='', null=True)),
            ],
            options={
                'db_table': 'gissmo_documentview',
                'managed': False,
            },
        ),
    ]
