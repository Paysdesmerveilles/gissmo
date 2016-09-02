# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intervention', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            [("""CREATE OR REPLACE FUNCTION gissmo_audit()
            RETURNS trigger AS $body$
            DECLARE
                name TEXT;
            BEGIN
                IF (TG_OP = 'UPDATE') THEN
                    name := TG_TABLE_NAME::TEXT || '_history';
                    EXECUTE format('INSERT INTO %I VALUES(($1).*)', name) USING OLD;
                    RETURN NEW;
                END IF;
            EXCEPTION
                WHEN data_exception THEN
                    RAISE WARNING '[gissmo_audit] - ERROR [DATA EXCEPTION] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                WHEN unique_violation THEN
                    RAISE WARNING '[gissmo_audit] - ERROR [UNIQUE] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                WHEN OTHERS THEN
                    RAISE WARNING '[gissmo_audit] - ERROR [OTHER] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                    RETURN NULL;
            END;
            $body$ LANGUAGE plpgsql;""")],
        ),
        migrations.RunSQL(
            [("""CREATE OR REPLACE FUNCTION place_place_clustering()
            RETURNS trigger AS $body$
            DECLARE
                intervention_id INTEGER;
            BEGIN
                IF (TG_OP = 'INSERT') AND (NEW.intervention_id IS NULL) THEN
                    INSERT INTO intervention_intervention (date, place_id, confirmed) VALUES (date_trunc('day', NEW.insert_datetime), NEW.id, False)
                        ON CONFLICT (date, place_id) DO NOTHING
                        RETURNING id
                    INTO intervention_id;
                    NEW.intervention_id := intervention_id;
                    RETURN NEW;
                END IF;
            EXCEPTION
                WHEN data_exception THEN
                    RAISE WARNING '[place_place_clustering] - ERROR [DATA EXCEPTION] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                WHEN unique_violation THEN
                    RAISE WARNING '[place_place_clustering] - ERROR [UNIQUE] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                WHEN OTHERS THEN
                    RAISE WARNING '[place_place_clustering] - ERROR - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                    RETURN NULL;
            END;
            $body$ LANGUAGE plpgsql;""")],
        ),
        migrations.RunSQL(
            [("""CREATE OR REPLACE FUNCTION have_place_id_field_clustering()
            RETURNS trigger AS $body$
            DECLARE
                intervention_id INTEGER;
            BEGIN
                IF (TG_OP = 'INSERT') AND (NEW.intervention_id IS NULL) THEN
                    INSERT INTO intervention_intervention (date, place_id, confirmed) VALUES (date_trunc('day', NEW.insert_datetime), NEW.place_id, False)
                        ON CONFLICT (date, place_id) DO NOTHING

                        RETURNING id
                    INTO intervention_id;
                    NEW.intervention_id := intervention_id;
                    RETURN NEW;
                END IF;
            EXCEPTION
                WHEN data_exception THEN
                    RAISE WARNING '[have_place_id_field_clustering] - ERROR [DATA EXCEPTION] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                WHEN unique_violation THEN
                    RAISE WARNING '[have_place_id_field_clustering] - ERROR [UNIQUE] - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                WHEN OTHERS THEN
                    RAISE WARNING '[have_place_id_field_clustering] - ERROR - SQLSTATE: %, SQLERRM: %',SQLSTATE,SQLERRM;
                    RETURN NULL;
            END;
            $body$ LANGUAGE plpgsql;""")],
        ),
    ]
