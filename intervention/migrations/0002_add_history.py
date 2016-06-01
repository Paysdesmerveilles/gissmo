# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            [("""CREATE TABLE equipment_type_history (
                type_id INTEGER,
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
            [("""CREATE TABLE equipment_equipment_history (
                equipment_id INTEGER,
                name VARCHAR(50),
                vendor VARCHAR(50),
                purchase_date DATE,
                clock_drift DOUBLE PRECISION,
                clock_drift_unit VARCHAR(50),
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
    ]
