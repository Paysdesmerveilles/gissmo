# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0005_add_document_history'),
        ('place', '0003_auto_20160523_0858'),
    ]

    operations = [
        # place_state
        migrations.RunSQL(
            [("""CREATE TABLE place_state_history (
                object_id INTEGER,
                code INTEGER,
                start TIMESTAMP,
                "end" TIMESTAMP,
                place_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT place_state_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER place_state_audit
            AFTER UPDATE ON place_state
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # place_groundtype
        migrations.RunSQL(
            [("""CREATE TABLE place_groundtype_history (
                object_id INTEGER,
                name VARCHAR(2),
                description VARCHAR(255),
                intervention_id INTEGER,
                CONSTRAINT groundtype_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER place_groundtype_audit
            AFTER UPDATE ON place_groundtype
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # place_place
        migrations.RunSQL(
            [("""CREATE TABLE place_place_history (
                object_id INTEGER,
                name VARCHAR(50),
                type INTEGER,
                description TEXT,
                creation_date DATE,
                note TEXT,
                address_street VARCHAR(100),
                address_zipcode VARCHAR(15),
                address_city VARCHAR(100),
                address_region VARCHAR(100),
                address_county VARCHAR(100),
                address_country VARCHAR(50),
                geology VARCHAR(50),
                contact TEXT,
                latitude NUMERIC(9,6),
                longitude NUMERIC(9,6),
                elevation NUMERIC(5,1),
                ground_type_id INTEGER,
                state_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT place_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER place_place_audit
            AFTER UPDATE ON place_place
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # place_placeoperator
        migrations.RunSQL(
            [("""CREATE TABLE place_placeoperator_history (
                object_id INTEGER,
                operator_id INTEGER,
                place_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT placeoperator_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER placeoperator_audit
            AFTER UPDATE ON place_placeoperator
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # place_placedocument
        migrations.RunSQL([("""CREATE TABLE place_placedocument_history (
                object_id INTEGER,
                document_id INTEGER,
                place_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT placedocument_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER placedocument_audit
            AFTER UPDATE ON place_placedocument
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
    ]
