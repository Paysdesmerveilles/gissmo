# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0007_add_project_history'),
        ('equipment', '0002_auto_20160531_0819'),
    ]

    operations = [
        # equipment_state
        migrations.RunSQL(
            [("""CREATE TABLE equipment_state_history (
                object_id INTEGER,
                code INTEGER,
                start TIMESTAMP,
                "end" TIMESTAMP,
                equipment_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_state_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_state_audit
            AFTER UPDATE ON equipment_state
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_type
        migrations.RunSQL(
            [("""CREATE TABLE equipment_type_history (
                object_id INTEGER,
                name VARCHAR(40),
                rank INTEGER,
                parent_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT type_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_type_audit
            AFTER UPDATE ON equipment_type
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_model
        migrations.RunSQL(
            [("""CREATE TABLE equipment_model_history (
                object_id INTEGER,
                name VARCHAR(50),
                rank INTEGER,
                manufacturer VARCHAR(50),
                chain_type INTEGER,
                is_network_model BOOLEAN,
                _type_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT model_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_model_audit
            AFTER UPDATE ON equipment_model
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_model_documents
        migrations.RunSQL(
            [("""CREATE TABLE equipment_model_documents_history (
                object_id INTEGER,
                model_id INTEGER,
                document_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_model_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        # equipment_equipment
        migrations.RunSQL(
            [("""CREATE TABLE equipment_equipment_history (
                object_id INTEGER,
                name VARCHAR(50),
                vendor VARCHAR(50),
                purchase_date DATE,
                clock_drift DOUBLE PRECISION,
                clock_drift_unit VARCHAR(15),
                storage_format VARCHAR(50),
                note TEXT,
                contact_id INTEGER,
                model_id INTEGER,
                owner_id INTEGER,
                place_id INTEGER,
                state_id INTEGER,
                last_edition TIMESTAMP,
                last_user_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_equipment_audit
            AFTER UPDATE ON equipment_equipment
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_equipment_cluster
            AFTER INSERT ON equipment_equipment_history
            FOR EACH ROW EXECUTE PROCEDURE have_place_id_field_clustering();""")],
        ),
        # equipment_equipment_documents
        migrations.RunSQL(
            [("""CREATE TABLE equipment_equipment_documents_history (
                object_id INTEGER,
                equipment_id INTEGER,
                document_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_documents_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_equipment_documents_audit
            AFTER UPDATE ON equipment_equipment_documents
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_forbiddenequipmentmodel
        migrations.RunSQL(
            [("""CREATE TABLE equipment_forbiddenequipmentmodel_history (
                object_id INTEGER,
                original_id INTEGER,
                recommended_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT forbiddenequipmentmodel_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_forbiddenequipmentmodel_audit
            AFTER UPDATE ON equipment_forbiddenequipmentmodel
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_parameter
        migrations.RunSQL(
            [("""CREATE TABLE equipment_parameter_history (
                object_id INTEGER,
                name VARCHAR(255),
                model_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_parameter_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_parameter_audit
            AFTER UPDATE ON equipment_parameter
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_value
        migrations.RunSQL(
            [("""CREATE TABLE equipment_value_history (
                object_id INTEGER,
                name VARCHAR(255),
                is_default BOOLEAN,
                parameter_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_value_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_value_audit
            AFTER UPDATE ON equipment_value
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_configuration
        migrations.RunSQL(
            [("""CREATE TABLE equipment_configuration_history (
                object_id INTEGER,
                parameter VARCHAR(255),
                value VARCHAR(255),
                start TIMESTAMP,
                "end" TIMESTAMP,
                equipment_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_configuration_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_configuration_audit
            AFTER UPDATE ON equipment_configuration
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_service
        migrations.RunSQL(
            [("""CREATE TABLE equipment_service_history (
                object_id INTEGER,
                protocol INTEGER,
                port INTEGER,
                description VARCHAR(256),
                equipment_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_service_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_service_audit
            AFTER UPDATE ON equipment_service
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # equipment_ipaddress
        migrations.RunSQL(
            [("""CREATE TABLE equipment_ipaddress_history (
                object_id INTEGER,
                ip VARCHAR(255),
                netmask INET,
                equipment_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT equipment_ipaddress_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER equipment_ipaddress_audit
            AFTER UPDATE ON equipment_ipaddress
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
    ]
