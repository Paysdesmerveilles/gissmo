#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# WARNING: Need to use python manage.py migrate first! To deploy new 2.0 version

import os

from peewee import *  # NOQA
from playhouse.pool import PooledPostgresqlExtDatabase

HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
DB = os.getenv('POSTGRES_DB', 'postgres')
USER = os.getenv('POSTGRES_USER', 'postgres')
PWD = os.getenv('POSTGRES_PASS', 'postgres')
PORT = os.getenv('DB_PORT_5432_TCP_PORT', '5432')


def main():
    db = PooledPostgresqlExtDatabase(
        DB,
        max_connections=32,
        stale_timeout=300,
        user=USER,
        password=PWD,
        host=HOST,
        port=PORT,
        register_hstore=False)

    try:
        # START
        db.connect()
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
            db.execute_sql(sql)

        # CHECKS
        # TODO: add some checks on database before
        # TODO: builttype: create an association between old types and new ones

        # SIMPLE MIGRATION
        # TODO: add tables that are just rename or with simple migration
        # - gissmo_equipsupertype -> equipment_type: SAME ID
        class GissmoSuperType(Model):
            id = IntegerField(db_column='id')
            name = CharField(db_column='equip_supertype_name')
            rank = IntegerField(db_column='presentation_rank')

            class Meta:
                database = db
                db_table = 'gissmo_equipsupertype'

        class Type(Model):
            name = CharField()
            rank = IntegerField()
            parent = ForeignKeyField('self', db_column='parent_id')

            class Meta:
                database = db
                db_table = 'equipment_type'

        link_equipment_supertype = {}
        for stype in GissmoSuperType.select().order_by(GissmoSuperType.id):
            s = Type.get_or_create(
                name=stype.name,
                rank=stype.rank)
            if isinstance(s, tuple):
                s = s[0]
            link_equipment_supertype[stype.id] = s.id

        # - gissmo_equiptype -> equipment_type (with parent): NEW IDS!!
        class GissmoType(Model):
            id = IntegerField(db_column='id')
            name = CharField(db_column='equip_type_name')
            rank = IntegerField(db_column='presentation_rank')
            supertype = ForeignKeyField(
                GissmoSuperType,
                db_column='equip_supertype_id')

            class Meta:
                database = db
                db_table = 'gissmo_equiptype'

        link_equipment_type = {}
        for _type in GissmoType.select().order_by(GissmoType.id):
            print("Equipment Type: %s (ID: %s)" % (_type.name, _type.id))
            t = Type.get_or_create(
                name=_type.name,
                rank=_type.rank)
            if isinstance(t, tuple):
                t = t[0]
            new = Type.get(Type.id == t)
            new.parent = _type.supertype
            new.save()
            link_equipment_type[_type.id] = new.id

        print("CORRELATION TYPE: %s" % link_equipment_type)

        # - gissmo_equipmodel -> equipment_model
        class GissmoModel(Model):
            """gissmo_equipmodel relation"""
            id = IntegerField(db_column='id')
            _type = ForeignKeyField(
                GissmoType,
                db_column='equip_type_id')
            name = CharField(db_column='equip_model_name')
            manufacturer = CharField()
            is_network_model = BooleanField(default=False)

            class Meta:
                database = db
                db_table = 'gissmo_equipmodel'

        class EquipmentModel(Model):
            name = CharField()
            rank = IntegerField()
            manufacturer = CharField()
            is_network_model = BooleanField()
            _type = ForeignKeyField(
                Type,
                db_column='_type_id')

            class Meta:
                database = db
                db_table = 'equipment_model'

        link_equipment_model = {}
        for e in GissmoModel.select().order_by(GissmoModel.id):
            print('Equipment Model: %s (ID: %s)' % (e.name, e.id))
            _type_id = link_equipment_type[e._type.id]
            t = Type.get(Type.id == _type_id)
            equipment = EquipmentModel.get_or_create(
                name=e.name,
                rank=0,
                manufacturer=e.manufacturer,
                is_network_model=e.is_network_model,
                _type=t)
            if isinstance(equipment, tuple):
                equipment = equipment[0]
            link_equipment_model[e.id] = equipment.id

        print("CORRELATION MODEL: %s" % link_equipment_model)

        # - gissmo_equipment -> equipment_equipment + state with intervention
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
        db.close()
        print("Connection closed.")
    except Exception as e:
        print("Unable to connect to the database: %s" % e)

if __name__ == "__main__":
    main()
