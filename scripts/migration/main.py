#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# WARNING: Need to use python manage.py migrate first! To deploy new 2.0 version

import psycopg2
import os

HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
DB = os.getenv('POSTGRES_DB', 'postgres')
USER = os.getenv('POSTGRES_USER', 'postgres')
PWD = os.getenv('POSTGRES_PASS', 'postgres')
PORT = os.getenv('DB_PORT_5432_TCP_PORT', '5432')


def main():
    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % (
        HOST,
        DB,
        USER,
        PWD,
        PORT)
    try:
        # START
        conn = psycopg2.connect(conn_string)
        print("Connected…")

        # CLEAN USELESS TABLES
        auth_message = "DROP TABLE IF EXISTS auth_message;"
        django_site = "DROP TABLE IF EXISTS django_site;"
        chainconfig_bck = "DROP TABLE IF EXISTS gissmo_chainconfig_bck;"
        equip_action = "DROP TABLE IF EXISTS gissmo_equipaction;"
        equip_state = "DROP TABLE IF EXISTS gissmo_equipstate;"
        paramequipmodel = "DROP TABLE IF EXISTS gissmo_paramequipmodel;"
        station_action = "DROP TABLE IF EXISTS gissmo_stationaction;"

        useless_tables_sql = [
            auth_message,
            django_site,
            chainconfig_bck,
            equip_action,
            equip_state,
            paramequipmodel,
            station_action]
        for sql in useless_tables_sql:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()

        # CHECKS
        # TODO: add some checks on database before
        # TODO: builttype: create an association between old types and new ones

        # SIMPLE MIGRATION
        # TODO: add tables that are just rename or with simple migration
        # - gissmo_equipment -> equipment_equipment + state with intervention
        # - gissmo_equipsupertype -> equipment_type: SAME ID
        try:
            cur = conn.cursor()
            cur.execute("""INSERT INTO equipment_type (id, name, rank) SELECT NEXTVAL('equipment_type_id_seq'), equip_supertype_name, presentation_rank FROM gissmo_equipsupertype;""")
            conn.commit()
            cur.close()
        except Exception as e:
            conn.rollback()
            print("gissmo_equipsupertype -> equipment_type: %s" % e)
        # - gissmo_equiptype -> equipment_type (with parent)
        try:
            cur = conn.cursor()
            cur.execute("""INSERT INTO equipment_type (id, name, rank, parent_id) SELECT NEXTVAL('equipment_type_id_seq'), equip_type_name, presentation_rank, equip_supertype_id FROM gissmo_equiptype;""")
            conn.commit()
            cur.close()
        except Exception as e:
            conn.rollback()
            print("gissmo_equiptype -> equipment_type: %s" % e)
        # - gissmo_equipmodel -> equipment_model
        # - gissmo_chainconfig -> equipment_configuration
        # - gissmo_datatype -> network_datatype
        # - gissmo_channel_data_type -> network_channel_datatypes
        # - gissmo_equipdoc -> document_document
        # - gissmo_equipmodeldoc -> document_document
        # - gissmo_equipdoctype -> document_type
        # - gissmo_equipmodeldoctype -> document_type
        # - gissmo_forbiddenequipmentmodel -> equipment_forbiddenequipmentmodel
        # - gissmo_intervdoc -> document_document
        # - gissmo_intervention -> intervention_intervention
        # - gissmo_intervorganism -> intervention_operator
        # - gissmo_intervuser -> intervention_protagonist
        # - gissmo_ipaddress -> equipment_ipaddress
        # - gissmo_network -> network_network
        # - gissmo_organism -> affiliation_organism
        # - gissmo_organism_users -> affiliation_organism_users
        # - gissmo_project -> project_project
        # - gissmo_project_sites -> project_project_places
        # - gissmo_services -> equipment_service
        # - gissmo_stationdoc -> document_document
        # - gissmo_stationdoctype -> document_type

        # SPECIFIC CASES
        # TODO: add specific cases
        # - gissmo_built -> place_place (with parent to station and site)
        # - gissmo_chain -> network_installation (with parents)
        # - gissmo_stationsite -> place_place
        # - gissmo_channel -> network_channel + equipment + place
        # - gissmo_intervequip -> intervention_equipmenthistory
        # - gissmo_intervstation -> intervention_stationhistory + place_place
        # - gissmo_parameterequip + parametervalue -> equipment_parameter + equipment_value

        # CLEAN DATABASE
        # TODO: delete all old gissmo_tablename tables
        # - gissmo_channelcode

        # END
        conn.close()
        print("Connection closed.")
    except Exception as e:
        print("Unable to connect to the database: %s" % e)

if __name__ == "__main__":
    main()