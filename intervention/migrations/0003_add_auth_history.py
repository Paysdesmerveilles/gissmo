# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0002_add_trigger'),
    ]

    operations = [
        # auth_group
        migrations.RunSQL(
            [("""CREATE TABLE auth_group_history (
                object_id INTEGER,
                name VARCHAR(80),
                intervention_id INTEGER,
                CONSTRAINT auth_group_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER auth_group_audit
            AFTER UPDATE ON auth_group
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # auth_user
        migrations.RunSQL(
            [("""CREATE TABLE auth_user_history (
                object_id INTEGER,
                username VARCHAR(30),
                first_name VARCHAR(30),
                last_name VARCHAR(30),
                email VARCHAR(254),
                password VARCHAR(128),
                is_staff BOOLEAN,
                is_active BOOLEAN,
                is_superuser BOOLEAN,
                last_login TIMESTAMP,
                date_joined TIMESTAMP,
                intervention_id INTEGER,
                CONSTRAINT user_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER auth_user_audit
            AFTER UPDATE ON auth_user
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # auth_user_groups
        migrations.RunSQL(
            [("""CREATE TABLE auth_user_groups_history (
                object_id INTEGER,
                user_id INTEGER,
                group_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT user_groups_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER auth_user_groups_audit
            AFTER UPDATE ON auth_user_groups
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
    ]
