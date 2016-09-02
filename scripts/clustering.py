#!/usr/bin/env python3

import os
import sys
import psycopg2

DEBUG = False

port = os.getenv('POSTGRES_PORT', 5432)

# Intervention requests
sql_existing_intervention = """
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


def info(s):
    """
    Just for printing elements. Sometimes not :)
    """
    if DEBUG:
        print("%s" % s)


def historyline_clustering(conn, history_lines, sql_update):
    """
    For each history line:
      * Check if intervention exists at same date and location (place).
      * If no one, create it.
      * Finally link history lines (without intervention) to intervention.
    """
    for history_line in history_lines:
        # search existing intervention with same date + place
        history_object = history_line[0]
        date = history_line[1]
        location = history_line[2]
        intervention = None

        existing_intervention = None
        with conn.cursor() as cur1:
            info("Check Interv. for Equipment ID: %s" % history_object)
            cur1.execute(
                sql_existing_intervention,
                (date, location,))

            existing_intervention = cur1.fetchone()
            if existing_intervention:
                info("Found!")
                intervention = existing_intervention[0]

        # if no existing intervention, create it!
        if not existing_intervention:
            info("Create Interv. for Equipment ID: %s" % history_object)
            created_intervention = None
            with conn.cursor() as cur2:
                cur2.execute(
                    sql_intervention_creation,
                    (date, location,))
                created_intervention = cur2.fetchone()[0]
            if created_intervention:
                intervention = created_intervention

        # check that we really have an intervention after that
        if not intervention:
            print("Error occured about intervention creation for this \
equipment ID: %s" % history_object)
            sys.exit(1)
        else:
            print("Equipment History '%s': using intervention '%s'" % (
                history_object, intervention))
        info("Intervention ID used: %s" % intervention)

        # finally UPDATE given equipment_history line with an intervention
        with conn.cursor() as cur3:
            print(history_line)
            print("SQL: %s. | %s | %s" % (sql_update, intervention, history_object))
            cur3.execute(sql_update, (intervention, history_object,))
            print("Equipment History '%s' updated." % history_object)


def main():
    """
    Connect to the database, check history tables by searching lines
    without intervention_id.
    Checks:
      * equipment_equipment_history
      * place_place_history
      * network_installation_histoyr
    """
    print("Used port: %s" % port)
    with psycopg2.connect(
        user="postgres",
        dbname="postgres",
        host="localhost",
            port=port) as conn:
        for table in [
            'equipment_equipment_history',
            'place_place_history',
                'network_installation_history']:
            place_field = 'place_id'
            if table == 'place_place_history':
                place_field = 'id'
            sql_without_intervention = """
                SELECT id, insert_datetime, %s
                FROM %s
                WHERE intervention_id IS NULL
                ORDER BY insert_datetime, %s""" % (
                    place_field,
                    table,
                    place_field)
            sql_update = "UPDATE %s" % (table,)
            sql_update += """
                SET intervention_id = %s
                WHERE id = %s;"""
            print(table, sql_update)
            # Do clustering on this element
            lines = []
            with conn.cursor() as curs:
                curs.execute(sql_without_intervention)
                lines = curs.fetchall()
            historyline_clustering(conn, lines, sql_update)
    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
