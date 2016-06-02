# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0006_add_place_history'),
        ('project', '0001_initial'),
    ]

    operations = [
        # project_project
        migrations.RunSQL(
            [("""CREATE TABLE project_project_history (
                group_id INTEGER,
                manager_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT project_history_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER project_project_audit
            AFTER UPDATE ON project_project
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
        # project_project_places
        migrations.RunSQL(
            [("""CREATE TABLE project_project_places_history (
                object_id INTEGER,
                project_id INTEGER,
                place_id INTEGER,
                intervention_id INTEGER,
                CONSTRAINT project_places_intervention_id_fk_intervention_id
                    FOREIGN KEY (intervention_id)
                    REFERENCES intervention_intervention (id),
                insert_datetime TIMESTAMP DEFAULT now() NOT NULL,
                id SERIAL);""")],
        ),
        migrations.RunSQL(
            [("""CREATE TRIGGER project_places_audit
            AFTER UPDATE ON project_project_places
            FOR EACH ROW EXECUTE PROCEDURE gissmo_audit();""")],
        ),
    ]
