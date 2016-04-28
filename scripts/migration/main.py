#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# WARNING: Need to use python manage.py migrate first! To deploy new 2.0 version
import pdb

from models import (
    db,
    EquipmentModel,
    GissmoGroundType,
    GissmoModel,
    GissmoNetwork,
    GissmoOrganism,
    GissmoSite,
    GissmoSuperType,
    GissmoType,
    GroundType,
    Network,
    Organism,
    Place,
    Station,
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


def fetch_or_migrate_groundtype():
    res = {}
    for ground in GissmoGroundType.select().order_by(GissmoGroundType.id):
        print("Ground type: %s (ID: %s)" % (ground.name, ground.id))
        g = GroundType.get_or_create(
            name=ground.name,
            description=ground.description)
        if isinstance(g, tuple):
            g = g[0]
        res[ground.id] = g.id
    return res


def create_place(site, organism, ground_types):
    types = {
        1: 3,  # STATION => MEASURE
        2: 1,  # OBSERVATOIRE => AGENCY
        3: 4,  # SAV => CUSTOMER SERVICE
        4: 0,  # NEANT => UNKNOWN
        5: 0,  # AUTRE => UNKNOWN
        6: 3,  # SITE_TEST => MEASURE
        7: 2,  # SITE_THEORIQUE => THEORITICAL
    }

    placename = site.name or site.code
    p = Place.create(
        name=placename,
        _type=types[site._type],
        latitude=site.latitude,
        longitude=site.longitude,
        elevation=site.elevation,
        operator=organism.id or None,
        description=site.description,
        creation_date=site.date,
        note=site.note,
        address_street=site.address,
        address_zipcode=site.zip_code,
        address_city=site.town,
        address_region=site.region,
        address_county=site.county,
        address_country=site.country,
        geology=site.geology,
        contact=site.contact)
    if isinstance(p, tuple):
        p = p[0]

    # Add ground type
    if site.ground_type:
        new_ground_type_id = ground_types[site.ground_type]
        if new_ground_type_id:
            g = GroundType.get(GroundType.id == new_ground_type_id)
            new = Place.get(Place.id == p.id)
            new.ground_type = g
            new.save()
    # Add parent
    if site.parent:
        to_link_to_parent.append(site.id)
    # Create station code linked to given place
    s = Station.get_or_create(
        code=site.code,
        description=site.station_description,
        operator=organism.id or None,
        place=p)
    if isinstance(s, tuple):
        s = s[0]

    return p


def fetch_or_migrate_site(ground_types, organisms):
    # Prepare some values
    res = {}

    global to_link_to_parent
    to_link_to_parent = []
    for site in GissmoSite.select().order_by(GissmoSite.id):
        print("Site: [%s] %s (ID: %s)" % (site.code, site.name, site.id))
        new_organism_id = organisms[site.operator.id]
        if isinstance(new_organism_id, tuple):
            new_organism_id = new_organism_id[0]
        o = Organism.get(Organism.id == new_organism_id)

        # Search a place with same longitude/latitude/elevation
        # If not: create place
        # If exists, attempt to link it to existing place
        if not site.longitude and not site.latitude:
            p = create_place(site, o, ground_types)
            res[site.id] = p.id
            continue
        else:
            same = Place.select().where(
                Place.longitude == site.longitude,
                Place.latitude == site.latitude,
                Place.elevation == site.elevation or None)
            if not same:
                p = create_place(site, o, ground_types)
                res[site.id] = p.id
                continue
            placename = site.name or site.code
            try:
                p = Place.get(
                    Place.name == placename,
                    Place.longitude == site.longitude,
                    Place.latitude == site.latitude)
                if isinstance(p, tuple):
                    p = p[0]
            except Place.DoesNotExist as e:
                print(e)
                # Means that another site exists with same latitude/longitude
                # So add parent on it
                p = create_place(site, o, ground_types)
                first_same_place = same[0]
                new = Place.get(Place.id == p.id)
                new.parent = first_same_place
                new.save()
            res[site.id] = p.id

    # Create link between child and parents
    print("LINKING place between them…")
    for site_id in to_link_to_parent:
        site = GissmoSite.get(GissmoSite.id == site_id)
        new = Place.get(Place.id == res[site_id])
        parent = Place.get(Place.id == res[site.parent])
        new.parent = parent
        new.save()
    return res


def fetch_or_migrate_network():
    res = {}
    for network in GissmoNetwork.select().order_by(GissmoNetwork.id):
        print("Network: [%s] %s (ID: %s)" % (network.code, network.name, network.id))
        n = Network.get_or_create(code=network.code)
        if isinstance(n, tuple):
            n = n[0]
        new = Network.get(Network.id == n.id)
        new.name = network.name
        new.description = network.description
        new.start = network.start
        new.end = network.end
        new.xml_historical_code = network.historical_code
        new.xml_alternate_code = network.alternate_code
        new.xml_restricted_status = network.status
        new.save()
        res[network.id] = n.id
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

        # - gissmo_groundtype -> place_groundtype
        link_ground_type = fetch_or_migrate_groundtype()
        print("CORRELATION GROUND TYPE: %s" % link_ground_type)

        # - gissmo_stationsite -> place_place
        link_place = fetch_or_migrate_site(link_ground_type, link_organism)
        print("CORRELATION PLACE: %s" % link_place)

        # - gissmo_network -> network_network
        link_network = fetch_or_migrate_network()
        print("CORRELATION NETWORK: %s" % link_network)

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
        # - gissmo_channel -> network_channel + equipment + place
        # - gissmo_intervequip -> intervention_equipmenthistory
        # - gissmo_intervstation -> intervention_stationhistory + place_place
        # - gissmo_parameterequip + parametervalue -> equipment_parameter + equipment_value
        # - last equipment state (last_state on gissmo_equipment)
        # - last equipment station (last_station_id on gissmo_equipment)

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
