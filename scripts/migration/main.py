#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# WARNING: Need to use python manage.py migrate first! To deploy new 2.0 version

from models import (
    db,
    EquipmentModel,
    GissmoModel,
    GissmoOrganism,
    GissmoSuperType,
    GissmoType,
    Organism,
    Type,
)


def delete_useless_tables():
    auth_message = "auth_message;"
    django_site = "django_site;"
    chainconfig_bck = "gissmo_chainconfig_bck;"
    equip_action = "gissmo_equipaction;"
    equip_state = "gissmo_equipstate;"
    paramequipmodel = "gissmo_paramequipmodel;"
    station_action = "gissmo_stationaction;"
    changemodel = "gissmo_changemodelmodification;"

    useless_tables_sql = [
        auth_message,
        django_site,
        chainconfig_bck,
        equip_action,
        equip_state,
        paramequipmodel,
        station_action,
        changemodel]
    for tablename in useless_tables_sql:
        db.execute_sql("DROP TABLE IF EXISTS %s;" % (tablename,))


def fetch_or_migrate_supertype():
    res = {}
    for stype in GissmoSuperType.select().order_by(GissmoSuperType.id):
        print("Equipment Supertype: %s (ID: %s)" % (stype.name, stype.id))
        s = Type.get_or_create(
            name=stype.name,
            rank=stype.rank)
        if isinstance(s, tuple):
            s = s[0]
        res[stype.id] = s.id
    return res


def fetch_or_migrate_type():
    res = {}
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
        res[_type.id] = new.id
    return res


def fetch_or_migrate_model(equipment_types):
    res = {}
    for e in GissmoModel.select().order_by(GissmoModel.id):
        print('Equipment Model: %s (ID: %s)' % (e.name, e.id))
        _type_id = equipment_types[e._type.id]
        t = Type.get(Type.id == _type_id)
        equipment = EquipmentModel.get_or_create(
            name=e.name,
            rank=0,
            manufacturer=e.manufacturer,
            is_network_model=e.is_network_model,
            _type=t)
        if isinstance(equipment, tuple):
            equipment = equipment[0]
        res[e.id] = equipment.id
    return res


def fetch_or_migrate_organism():
    res = {}
    for organism in GissmoOrganism.select().order_by(GissmoOrganism.id):
        print("Organism: %s (ID: %s)" % (organism.name, organism.id))
        # object creation (if needed)
        o = Organism.get_or_create(
            name=organism.name,
            _type=organism._type)
        if isinstance(o, tuple):
            o = o[0]
        # add parent if needed
        if organism.parent:
            parent = Organism.get(Organism.id == organism.parent.id)
            new = Organism.get(Organism.id == o.id)
            new.parent = parent
            new.save()
        # keep link between old organism and new one
        res[organism.id] = o.id
    return res


def main():
    try:
        # START
        db.connect()
        print("Connected…")

        # CLEAN USELESS TABLES
        delete_useless_tables()

        # CHECKS
        # TODO: add some checks on database before
        # TODO: builttype: create an association between old types and new ones

        # SIMPLE MIGRATION
        # TODO: add tables that are just rename or with simple migration
        # - gissmo_equipsupertype -> equipment_type: SAME ID
        link_equipment_supertype = fetch_or_migrate_supertype()
        print("CORRELATION SUPERTYPE: %s" % link_equipment_supertype)

        # - gissmo_equiptype -> equipment_type (with parent): NEW IDS!!
        link_equipment_type = fetch_or_migrate_type()
        print("CORRELATION TYPE: %s" % link_equipment_type)

        # - gissmo_equipmodel -> equipment_model
        link_equipment_model = fetch_or_migrate_model(link_equipment_type)
        print("CORRELATION MODEL: %s" % link_equipment_model)

        # - gissmo_organism -> affiliation_organism
        link_organism = fetch_or_migrate_organism()
        print("CORRELATION ORGANISM: %s" % link_organism)

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
        # - last equipment state
        # - last station state

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
