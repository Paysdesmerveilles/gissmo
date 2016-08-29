#!/usr/bin/env python3

import os
import sys
import psycopg2

DEBUG = False

port = os.getenv('DB_PORT_5432_TCP_PORT', 5432)
sql_equipment_without_intervention = """
SELECT id, insert_datetime, place_id
FROM equipment_equipment_history
WHERE intervention_id IS NULL
ORDER BY insert_datetime, place_id;
"""
sql_intervention_regarding_criteria = """
SELECT id
FROM intervention_intervention
WHERE date = %s
AND place_id = %s;
"""
sql_intervention_creation = """
INSERT INTO intervention_intervention (date, place_id, confirmed)
VALUES (%s, %s, False)
RETURNING id;
"""
sql_equipment_update = """
UPDATE equipment_equipment_history
SET intervention_id = %s
WHERE id = %s;
"""


def info(s):
    if DEBUG:
        print("%s" % s)

print("Used port: %s" % port)

with psycopg2.connect(
    user="postgres",
    dbname="postgres",
    host="localhost",
        port=port) as conn:
    with conn.cursor() as curs:
        curs.execute(sql_equipment_without_intervention)
        for equip_change in curs.fetchall():
            # search existing intervention
            e = equip_change[0]
            date = equip_change[1]
            station_id = equip_change[2]
            intervention = None

            existing_intervention = None
            with conn.cursor() as cur1:
                info("Check Interv. for Equipment ID: %s" % e)
                cur1.execute(
                    sql_intervention_regarding_criteria,
                    (date, station_id,))

                existing_intervention = cur1.fetchone()
                if existing_intervention:
                    info("Found!")
                    intervention = existing_intervention[0]

            if not existing_intervention:
                info("Create Interv. for Equipment ID: %s" % e)
                created_intervention = None
                with conn.cursor() as cur2:
                    cur2.execute(
                        sql_intervention_creation,
                        (date, station_id,))
                    created_intervention = cur2.fetchone()[0]
                if created_intervention:
                    intervention = created_intervention

            if not intervention:
                print("Error occured about intervention creation for this \
equipment ID: %s" % e)
                sys.exit(1)
            else:
                print("Equipment History '%s': using intervention '%s'" % (
                    e, intervention))
            info("Intervention ID used: %s" % intervention)

            with conn.cursor() as cur3:
                cur3.execute(sql_equipment_update, (intervention, e,))
                print("Equipment History '%s' updated." % e)

conn.close()

sys.exit(0)
