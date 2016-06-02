# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0003_add_auth_history'),
        ('affiliation', '0001_initial'),
    ]

    operations = [
        # affiliation_agency
        migrations.RunSQL(
            [("""CREATE TABLE affiliation_agency_history (
                object_id INTEGER,
                name VARCHAR(255),
                _type INTEGER,
                parent_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT agency_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER agency_audit
            AFTER UPDATE ON affiliation_agency
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # affiliation_agency_users
        migrations.RunSQL(
            [("""CREATE TABLE affiliation_agency_users_history (
                object_id INTEGER,
                agency_id INTEGER,
                user_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT agency_users_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER agency_users_audit
                AFTER UPDATE ON affiliation_agency_users
                FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
    ]
