# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0004_add_affiliation_history'),
        ('document', '0001_initial'),
    ]

    operations = [
        # document_type
        migrations.RunSQL(
            [("""CREATE TABLE document_type_history (
                object_id INTEGER,
                name VARCHAR(40),
                intervention_id INTEGER,
                CONSTRAINT document_type_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER document_type_audit
            AFTER UPDATE ON document_type
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # document_document
        migrations.RunSQL(
            [("""CREATE TABLE document_document_history (
                object_id INTEGER,
                title VARCHAR(40),
                date DATE,
                private_link VARCHAR(200),
                start DATE,
                "end" DATE,
                _file VARCHAR(100),
                _type_id INTEGER,
                owner_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT document_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER document_audit
            AFTER UPDATE ON document_document
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
    ]
