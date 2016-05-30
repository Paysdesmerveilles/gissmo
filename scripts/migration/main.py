#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# WARNING: Need to use python manage.py migrate first! To deploy new 2.0 version
import pdb

from models import (
    AuthUser,
    Built,
    Configuration,
    db,
    Datatype,
    Equipment,
    EquipmentModel,
    GissmoBuilt,
    GissmoChainConfig,
    GissmoDatatype,
    GissmoEquipment,
    GissmoGroundType,
    GissmoIntervEquip,
    GissmoModel,
    GissmoNetwork,
    GissmoOrganism,
    GissmoParameter,
    GissmoProject,
    GissmoSite,
    GissmoSuperType,
    GissmoType,
    GissmoValue,
    GroundType,
    Network,
    Agency,
    Parameter,
    Place,
    PlaceOperator,
    Project,
    Station,
    Type,
    Value,
)


manager_username = 'maxime.besdeberc'


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


def fetch_or_migrate_agency():
    res = {}
    for agency in GissmoOrganism.select().order_by(GissmoOrganism.id):
        print("Agency: %s (ID: %s)" % (agency.name, agency.id))
        # object creation (if needed)
        a = Agency.get_or_create(
            name=agency.name,
            _type=agency._type)
        if isinstance(a, tuple):
            a = a[0]
        # add parent if needed
        if agency.parent:
            parent = Agency.get(Agency.name == agency.parent.name)
            new = Agency.get(Agency.id == a.id)
            new.parent = parent
            new.save()
        # keep link between old agency and new one
        res[agency.id] = a.id
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


def link_place_to_agency(place, agency):
    # Link place to agency (operator)
    link_exist = PlaceOperator.select().where(
        (PlaceOperator.operator_id == agency.id) &
        (PlaceOperator.place_id == place.id))
    if not link_exist:
        PlaceOperator.create(
            place=place,
            operator=agency)
    return


def create_place(site, placename, _type, types, ground_types):
    res = None
    new_type = types[site._type]
    if _type is not None:
        new_type = _type
    res = Place.create(
        name=placename,
        _type=new_type,
        latitude=site.latitude,
        longitude=site.longitude,
        elevation=site.elevation,
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
    if isinstance(res, tuple):
        res = res[0]

    # Add ground type
    if site.ground_type:
        new_ground_type_id = ground_types[site.ground_type]
        if new_ground_type_id:
            g = GroundType.get(GroundType.id == new_ground_type_id)
            new = Place.get(Place.id == res.id)
            new.ground_type = g
            new.save()

    return res


def get_or_create_place(site, agency, ground_types, _type=None):
    types = {
        1: None,  # STATION => Station + "production" state
        2: 18,  # OBSERVATOIRE => Agency + "undefined" warehouse place
        3: 1,  # SAV => CUSTOMER SERVICE
        4: 0,  # NEANT => UNKNOWN
        5: 0,  # AUTRE => UNKNOWN
        6: None,  # SITE_TEST => Station + "test" state
        7: None,  # SITE_THEORIQUE => Station + "theoritical" state
    }

    res = None
    placename = site.name or site.code
    if _type is not None and _type == 0:
        placename = 'Undefined %s' % placename[:40]
    # Check that place doesn't exist with same name
    try:
        same_name = Place.get(Place.name == placename)
    except Place.DoesNotExist:
        same_name = False
    try:
        same_localisation = Place.get(
            Place.name == placename,
            Place.longitude == site.longitude,
            Place.latitude == site.latitude)
    except Place.DoesNotExist:
        same_localisation = False
    if same_name and same_localisation:
        # place exists! return it
        if isinstance(same_name, tuple):
            same_name = same_name[0]
        res = same_name
    else:
        # Create Place
        p = create_place(site, placename, _type, types, ground_types)
        res = p

    # Link place to agency (operator)
    link_place_to_agency(res, agency)
    return res


def get_or_create_agency(observatory):
    code = observatory.code
    # some specific checks
    if code == 'DTINSU':
        code = 'DT INSU'
    elif code == 'OMP (Tarbes)':
        code = 'OMP-TARBES'
    # check if Agency exists
    res = Agency.select().where(Agency.name == code)
    if res:
        res = res[0]
    if not res:
        res = Agency.create(
            name=code,
            _type=0)
        if isinstance(res, tuple):
            res = res[0]
    return res


def check_site_builts(station, agencies, ground_types):
    res = None
    # If equipments are located on this site but without Built,
    # so create a 'Undefined' place with same latitude/longitude/elevation
    station_equipments = GissmoEquipment.select().where(
        GissmoEquipment.station == station.id)
    if station_equipments:
        interventions = GissmoIntervEquip.select().where(
            (GissmoIntervEquip.equip << station_equipments) &
            (GissmoIntervEquip.built.is_null(True))).count()
        if interventions > 0:
            # create 'Undefined' place with same code as this station
            undefined = 0
            agency_id = agencies[station.operator.id]
            agency = Agency.get(Agency.id == agency_id)
            p = get_or_create_place(
                station,
                agency,
                ground_types,
                _type=undefined)
            if isinstance(p, tuple):
                p = p[0]

            # As place have been create, return it
            res = p
    return res


def fetch_or_migrate_site(ground_types, agencies):
    # Prepare some values
    observatories = {}
    stations = {}
    places = {}
    states = {
        1: 2,  # Measurement site => production
        6: 1,  # Test site => test
        7: 0,  # Theoritical site => theoritical
    }

    # Check observatories
    old_obs = GissmoSite.select().where(
        GissmoSite._type == 2).order_by(GissmoSite.id)
    for obs in old_obs:
        print("Site [OBS]: [%s] %s (ID: %s)" % (obs.code, obs.name, obs.id))
        a = get_or_create_agency(obs)
        observatories[obs.id] = a.id
        # check if parent exists. If not, create it.
        if obs.parent:
            print("¦- parent detected")
            parent = GissmoSite.get(GissmoSite.id == obs.parent)
            if isinstance(parent, tuple):
                parent = parent[0]
            parent_a = get_or_create_agency(parent)
            observatories[parent.id] = parent_a.id
            new = Agency.get(Agency.id == a.id)
            new.parent = parent_a
            new.save()

    # Then places
    old_places = GissmoSite.select().where(
        GissmoSite._type << [3, 4, 5]).order_by(GissmoSite.id)
    for place in old_places:
        print("Site [PLACE]: [%s] %s (ID: %s)" % (
            place.code, place.name, place.id))
        agency_id = agencies[place.operator.id]
        agency = Agency.get(Agency.id == agency_id)
        p = get_or_create_place(place, agency, ground_types)
        if isinstance(p, tuple):
            p = p[0]
        places[place.id] = p.id

    # Finally stations
    old_stations = GissmoSite.select().where(
        GissmoSite._type << [1, 6, 7]).order_by(GissmoSite.id)
    for station in old_stations:
        print("Site [STATION]: [%s] %s (ID: %s)" % (
            station.code, station.name, station.id))
        # Note: After migration, GISSMO 2.0 can have 2 stations with same code
        # But the database from which we come have no doublons.
        # So migration is safe about this
        s = Station.get_or_create(code=station.code)
        if isinstance(s, tuple):
            s = s[0]
        new = Station.get(Station.id == s.id)
        new.description = station.name
        new.state = states[station._type]
        new.latitude = station.latitude
        new.longitude = station.longitude
        new.elevation = station.elevation
        new.save()

        stations[station.id] = s.id

        have_built = check_site_builts(station, agencies, ground_types)
        if have_built:
            # remember place
            places[station.id] = have_built

            # Link station to the place
            Built.get_or_create(
                place=have_built,
                station=s)

    return observatories, stations, places


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


def get_builttype(name):
    res = 0
    types = {
        '01. Tunnel': 2,
        '02. Galerie': 3,
        '04. Drain': 4,
        '05. Grotte': 5,
        '06. Cave': 6,
        '07. Sous sol': 7,
        '08. Armoire': 8,
        '09. Caisson': 9,
        '10. Préfabriqué': 10,
        '11. Local': 11,
        '12. Fort militaire': 12,
        '13. Radier': 13,
        '14. Dalle': 14,
        '15. Exterieur': 15,
        '03. Puits sismique': 16,
        'Autre': 0,
        '16. Forage': 17,
    }
    if name in types:
        return types[name]
    return res


def fetch_or_migrate_built(agencies):
    res = {}
    for built in GissmoBuilt.select().order_by(GissmoBuilt.id):
        print("Built: %s (ID: %s)" % (built.name, built.id))
        builttype = get_builttype(built._type.name)
        builtname = built.name or 'Unknown'
        # Builts have same operator as those from the linked StationSite
        o = built.station.operator
        p = Place.get_or_create(
            name=builtname,
            _type=builttype,
            note=built.note)
        if isinstance(p, tuple):
            p = p[0]

        # Link place to agency (operator)
        agency_id = agencies[o.id]
        agency = Agency.get(Agency.id == agency_id)
        link_place_to_agency(p, agency)

        # Link built to its station
        try:
            have_station = Station.get(Station.code == built.station.code)
        except Station.DoesNotExist:
            have_station = False
        if have_station:
            if isinstance(have_station, tuple):
                have_station = have_station[0]
            Built.get_or_create(
                place=p,
                station=have_station)

        res[built.id] = p.id
    return res


def search_place_from_station_id(station_id, equip, places, agencies, ground_types, builts):
    """
    As we comme from fetch_or_migrate_equipment we know that:
      - our station doesn't have any linked place
      - but our equipment is linked to this station_id
    First we check intervention for the given station and equipment. If last
    one contains a built: check if exists. If not create it. And then link to
    it.
    Then if nothing found, create a place for the given Station with
    "undefined" and link the place to agency and add it to "places" dict.
    """
    res = None
    old_station = GissmoSite.get(GissmoSite.id == station_id)
    # first check interventions
    intervention = GissmoIntervEquip.select().where(
        (GissmoIntervEquip == equip.id) &
        (GissmoIntervEquip.station == station_id)
    ).order_by(-GissmoIntervEquip.id).first()
    if intervention and intervention.built and intervention.built.id in builts:
        built_id = builts[intervention.built.id]
        built = Place.get(Place.id == built_id)
        res = built
    else:
        agency_id = agencies[old_station.operator.id]
        agency = Agency.get(Agency.id == agency_id)
        p = get_or_create_place(old_station, agency, ground_types)
        if isinstance(p, tuple):
            p = p[0]
        res = p
    return res


def fetch_or_migrate_equipment(places, agencies, models, ground_types, builts):
    """
    For each equipment checks interventions.
    Last one define the built or the station on which this equipment is.
    """
    res = {}
    for equip in GissmoEquipment.select().order_by(GissmoEquipment.id):
        print("Equipment: %s (ID: %s)" % (equip.name, equip.id))
        model_id = models[equip.model.id]
        owner_id = agencies[equip.owner.id]
        station_id = equip.station
        neant = Place.get(Place.name == 'NEANT')
        # moves equipment in "NEANT" if no station_id
        if station_id and station_id in places:
            place = Place.get(Place.id == places[station_id])
            if isinstance(place, tuple):
                place = place[0]
        elif station_id:
            place = search_place_from_station_id(station_id, equip, places, agencies, ground_types, builts)
        else:
            place = neant

        m = EquipmentModel.get(EquipmentModel.id == model_id)
        o = Agency.get(Agency.id == owner_id)
        e = Equipment.get_or_create(
            name=equip.name,
            model=m,
            owner=o,
            place=place)
        if isinstance(e, tuple):
            e = e[0]
        if equip.vendor or equip.purchase_date or equip.note or equip.contact:
            new = Equipment.get(Equipment.id == e.id)
            new.vendor = equip.vendor
            new.purchase_date = equip.purchase_date
            new.note = "\n".join([equip.note or '', equip.contact or ''])
            new.save()

        res[equip.id] = e.id
    return res


def fetch_or_migrate_datatype():
    res = {}
    for _type in GissmoDatatype.select().order_by(GissmoDatatype.id):
        d = Datatype.get_or_create(
            name=_type.name)
        if isinstance(d, tuple):
            d = d[0]
        res[_type.id] = d.id
    return res


def migrate_project():
    """
    As groups and users are both in same tables, we don't need to do any check
    """
    for project in GissmoProject.select():
        print("Project group id: %s" % project.group.id)
        m = None
        if not project.manager:
            m = AuthUser.get(AuthUser.username == manager_username)
        else:
            m = project.manager
        p = Project.get_or_create(
            group=project.group,
            manager=m)
        if isinstance(p, tuple):
            p = p[0]


def fetch_or_migrate_parameter(models):
    res = {}
    for parameter in GissmoParameter.select().order_by(GissmoParameter.id):
        print("Parameter: %s (ID: %s)" % (parameter.name, parameter.id))
        m = EquipmentModel.get(EquipmentModel.id == models[parameter.model.id])
        p = Parameter.get_or_create(
            name=parameter.name,
            model=m)
        if isinstance(p, tuple):
            p = p[0]
        res[parameter.id] = p.id
    return res


def fetch_or_migrate_value(params):
    res = {}
    for value in GissmoValue.select().order_by(GissmoValue.id):
        p = Parameter.get(Parameter.id == params[value.parameter.id])
        v = Value.get_or_create(
            name=value.name,
            is_default=value.is_default,
            parameter=p)
        if isinstance(v, tuple):
            v = v[0]
        res[value.id] = v.id
    return res


def fetch_or_migrate_configuration(equipments):
    res = {}
    for config in GissmoChainConfig.select().order_by(GissmoChainConfig.id):
        print("Configuration: %s/%s (ID: %s)" % (
            config.parameter.name,
            config.value.name,
            config.id))
        e = Equipment.get(Equipment.id == equipments[config.chain.equipment.id])
        c = Configuration.get_or_create(
            parameter=config.parameter.name,
            value=config.value.name,
            equipment=e)
        if isinstance(c, tuple):
            c = c[0]
        res[config.id] = c.id
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

        # MIGRATION
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

        # - gissmo_organism -> affiliation_agency
        link_agency = fetch_or_migrate_agency()
        print("CORRELATION AGENCY: %s" % link_agency)

        # - gissmo_groundtype -> place_groundtype
        link_ground_type = fetch_or_migrate_groundtype()
        print("CORRELATION GROUND TYPE: %s" % link_ground_type)

        # - gissmo_stationsite -> place_place + network_station
        link_observatory, link_station, link_place = \
            fetch_or_migrate_site(link_ground_type, link_agency)
        print("CORRELATION OBS: %s" % link_observatory)
        print("CORRELATION STATION: %s" % link_station)
        print("CORRELATION PLACE: %s" % link_place)

        # - gissmo_network -> network_network
        link_network = fetch_or_migrate_network()
        print("CORRELATION NETWORK: %s" % link_network)

        # - gissmo_built -> place_place
        link_built = fetch_or_migrate_built(link_agency)
        print("CORRELATION BUILT: %s" % link_built)

        # - gissmo_equipment -> equipment_equipment
        link_equipment = fetch_or_migrate_equipment(link_place, link_agency, link_equipment_model, link_ground_type, link_built)
        print("CORRELATION EQUIPMENT: %s" % link_equipment)

        # - gissmo_datatype -> network_datatype
        link_datatype = fetch_or_migrate_datatype()
        print("CORRELATION DATATYPE: %s" % link_datatype)

        # - gissmo_project -> project_project
        migrate_project()
        print("PROJECTS migrated")

        # - gissmo_parameterequip -> equipment_parameter
        link_parameter = fetch_or_migrate_parameter(link_equipment_model)
        print("CORRELATION PARAMETER: %s" % link_parameter)

        # - gissmo_parametervalue -> equipment_value
        link_value = fetch_or_migrate_value(link_parameter)
        print("CORRELATION VALUE: %s" % link_value)

        # - gissmo_chainconfig -> equipment_configuration
        link_configuration = fetch_or_migrate_configuration(link_equipment)
        print("CORRELATION CONFIGURATION: %s" % link_configuration)

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
        # - gissmo_organism_users -> affiliation_agency_users
        # - gissmo_project_sites -> project_project_places
        # - gissmo_services -> equipment_service
        # - gissmo_stationdoc -> document_document
        # - gissmo_stationdoctype -> document_type

        # SPECIFIC CASES
        # TODO: add specific cases
        # - gissmo_chain -> network_installation (with parents)
        # - gissmo_channel -> network_channel + equipment + place
        # - gissmo_intervequip -> intervention_equipmenthistory
        # - gissmo_intervstation -> intervention_stationhistory + place_place
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
