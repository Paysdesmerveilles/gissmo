# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0008_add_equipment_history'),
        ('network', '0003_remove_station_operator'),
    ]

    operations = [
        # network_station
        migrations.RunSQL(
            [("""CREATE TABLE network_station_history (
                object_id INTEGER,
                code VARCHAR(40),
                description TEXT,
                state INTEGER,
                elevation NUMERIC(5,1),
                latitude NUMERIC(9,6),
                longitude NUMERIC(9,6),
                intervention_id INTEGER,
                CONSTRAINT network_station_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_station_audit
            AFTER UPDATE ON network_station
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # network_station_documents
        migrations.RunSQL(
            [("""CREATE TABLE network_station_documents_history (
                object_id INTEGER,
                station_id INTEGER,
                document_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT network_station_documents_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_station_documents_audit
            AFTER UPDATE ON network_station_documents
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # network_built
        migrations.RunSQL(
            [("""CREATE TABLE network_built_history (
                object_id INTEGER,
                place_id INTEGER,
                station_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT network_built_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_built_audit
            AFTER UPDATE ON network_built
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # network_network
        migrations.RunSQL(
            [("""CREATE TABLE network_network_history (
                object_id INTEGER,
                code VARCHAR(5),
                name VARCHAR(50),
                description TEXT,
                start TIMESTAMP,
                "end" TIMESTAMP,
                intervention_id INTEGER,
                CONSTRAINT network_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_network_audit
            AFTER UPDATE ON network_network
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # network_installation
        migrations.RunSQL(
            [("""CREATE TABLE network_installation_history (
                object_id INTEGER,
                _type INTEGER,
                start TIMESTAMP,
                "end" TIMESTAMP,
                depth NUMERIC(4,1),
                latitude NUMERIC(9,6),
                longitude NUMERIC(9,6),
                elevation NUMERIC(5,1),
                equipment_id INTEGER,
                parent_id INTEGER,
                place_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT network_installation_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_installation_audit
            AFTER UPDATE ON network_installation
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_installation_cluster
            AFTER INSERT ON network_installation_history
            FOR EACH ROW EXECUTE PROCEDURE have_place_id_field_clustering();""")],
        ),
        # network_datatype
        migrations.RunSQL(
            [("""CREATE TABLE network_datatype_history (
                object_id INTEGER,
                name VARCHAR(50),
                intervention_id INTEGER,
                CONSTRAINT network_datatype_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_datatype_audit
            AFTER UPDATE ON network_datatype
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # network_channel
        migrations.RunSQL(
            [("""CREATE TABLE network_channel_history (
                object_id INTEGER,
                code INTEGER,
                location_code VARCHAR(2),
                azimuth NUMERIC(4,1),
                dip NUMERIC(3,1),
                sample_rate DOUBLE PRECISION,
                start TIMESTAMP,
                "end" TIMESTAMP,
                description TEXT,
                calibration_unit INTEGER,
                latitude NUMERIC(9,6),
                longitude NUMERIC(9,6),
                elevation NUMERIC(5,1),
                installation_id INTEGER,
                network_id INTEGER,
                station_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT network_channel_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_channel_audit
            AFTER UPDATE ON network_channel
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # network_channel_datatypes
        migrations.RunSQL(
            [("""CREATE TABLE network_channel_datatypes_history (
                object_id INTEGER,
                channel_id INTEGER,
                datatype_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT network_channel_datatypes_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_channel_datatypes_audit
            AFTER UPDATE ON network_channel_datatypes
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # network_channel_configurations
        migrations.RunSQL(
            [("""CREATE TABLE network_channel_configurations_history (
                object_id INTEGER,
                channel_id INTEGER,
                configuration_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT network_channel_configurations_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
             id SERIAL);""")]
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER network_channel_configurations_audit
            AFTER UPDATE ON network_channel_configurations
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
    ]
