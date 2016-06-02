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
    ]
