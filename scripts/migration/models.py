import os
from datetime import datetime

from peewee import (
    BooleanField,
    CharField,
    CompositeKey,
    DateField,
    DateTimeField,
    DecimalField,
    DoubleField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)
from playhouse.pool import PooledPostgresqlExtDatabase

HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
DB = os.getenv('POSTGRES_DB', 'postgres')
USER = os.getenv('POSTGRES_USER', 'postgres')
PWD = os.getenv('POSTGRES_PASS', 'postgres')
PORT = os.getenv('POSTGRES_PORT', '5432')

db = PooledPostgresqlExtDatabase(
    DB,
    max_connections=32,
    stale_timeout=300,
    user=USER,
    password=PWD,
    host=HOST,
    port=PORT,
    register_hstore=False)


class AuthUser(Model):
    id = IntegerField(db_column='id')
    username = CharField()

    class Meta:
        database = db
        db_table = 'auth_user'


class AuthGroup(Model):
    id = IntegerField(db_column='id')

    class Meta:
        database = db
        db_table = 'auth_group'


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

agency_choices = (
    (0, 'Observatory/Laboratory'),
    (1, 'Network'),
    (2, 'Business'),
    (3, 'Customer service company'),
    (4, 'Unknown'),
)


class GissmoOrganism(Model):
    id = IntegerField(db_column='id')
    name = CharField()
    _type = IntegerField(choices=agency_choices)
    parent = ForeignKeyField(
        'self',
        null=True,
        db_column='parent_id')

    class Meta:
        database = db
        db_table = 'gissmo_organism'


class Agency(Model):
    name = CharField()
    _type = IntegerField(choices=agency_choices)
    parent = ForeignKeyField(
        'self',
        null=True,
        db_column='parent_id')

    def __str__(self):
        return '%s' % self.name

    class Meta:
        database = db
        db_table = 'affiliation_agency'


class GissmoEquipment(Model):
    id = IntegerField(db_column='id')
    model = ForeignKeyField(
        GissmoModel,
        db_column='equip_model_id')
    name = CharField(db_column='serial_number')
    owner = ForeignKeyField(
        GissmoOrganism,
        db_column='owner_id')
    vendor = CharField()
    contact = TextField()
    note = TextField()
    purchase_date = DateField()
    state = IntegerField(db_column='last_state')
    station = IntegerField(db_column='last_station_id')

    class Meta:
        database = db
        db_table = 'gissmo_equipment'


class GissmoIntervention(Model):
    station = IntegerField(db_column='station_id')
    date = DateTimeField(db_column='intervention_date')

    class Meta:
        database = db
        db_table = 'gissmo_intervention'


class GissmoIntervEquip(Model):
    id = IntegerField(db_column='id')
    equip = IntegerField(db_column='equip_id')
    built = IntegerField(db_column='built_id')
    station = IntegerField(db_column='station_id')

    class Meta:
        database = db
        db_table = 'gissmo_intervequip'


class GissmoGroundType(Model):
    id = IntegerField(db_column='id')
    name = CharField()
    description = CharField()

    class Meta:
        database = db
        db_table = 'gissmo_groundtype'


class GroundType(Model):
    name = CharField()
    description = CharField()

    class Meta:
        database = db
        db_table = 'place_groundtype'


class GissmoSite(Model):
    """gissmo_stationsite relation"""
    id = IntegerField(db_column='id')
    _type = IntegerField(db_column='site_type')
    code = CharField(db_column='station_code')
    name = CharField(db_column='site_name')
    latitude = DecimalField(max_digits=8, decimal_places=6)
    longitude = DecimalField(max_digits=9, decimal_places=6)
    elevation = DecimalField(max_digits=5, decimal_places=1)
    operator = ForeignKeyField(GissmoOrganism, db_column='operator_id')
    address = CharField()
    town = CharField()
    county = CharField()
    region = CharField()
    country = CharField()
    zip_code = CharField()
    contact = TextField()
    note = TextField()
    private_link = CharField()
    parent = IntegerField(db_column='station_parent_id')
    geology = CharField()
    status = IntegerField(db_column='restricted_status')  # XML status
    alternate_code = CharField()  # XML alternate code
    historical_code = CharField()  # XML historical code
    description = TextField(db_column='site_description')
    station_description = TextField()
    # WARNING: We omit all _unit, _pluserror, _minuserror and _datum fields
    date = DateField(db_column='creation_date')
    state = IntegerField(db_column='last_state')
    ground_type = IntegerField(db_column='ground_type_id')

    class Meta:
        database = db
        db_table = 'gissmo_stationsite'


place_choices = (
    (0, 'Unknown'),
    (1, 'Customer service place'),
    (2, 'Tunnel'),
    (3, 'Drift'),
    (4, 'Drain'),
    (5, 'Cave'),
    (6, 'Cellar'),
    (7, 'Underground'),
    (8, 'Cabinet'),
    (9, 'Chamber'),
    (10, 'Prefabricated'),
    (11, 'Premises'),
    (12, 'Fort'),
    (13, 'Apron'),
    (14, 'Slab'),
    (15, 'Outside'),
    (16, 'Well'),
    (17, 'Drilling'),
    (18, 'Warehouse'),
)


class Place(Model):
    _type = IntegerField(choices=place_choices)
    name = CharField()
    description = TextField()
    creation_date = DateField()
    note = TextField()
    address_street = CharField()
    address_zipcode = CharField()
    address_city = CharField()
    address_region = CharField()
    address_county = CharField()
    address_country = CharField()
    geology = CharField()
    contact = TextField()
    latitude = DecimalField(max_digits=9, decimal_places=6)
    longitude = DecimalField(max_digits=9, decimal_places=6)
    elevation = DecimalField(max_digits=5, decimal_places=1)
    ground_type = ForeignKeyField(GroundType, db_column='ground_type_id')

    class Meta:
        database = db
        db_table = 'place_place'


class PlaceOperator(Model):
    place = ForeignKeyField(Place, db_column='place_id')
    operator = ForeignKeyField(Agency, db_column='operator_id')

    class Meta:
        database = db
        db_table = 'place_placeoperator'


class State(Model):
    code = IntegerField()
    start = DateTimeField()
    end = DateTimeField()
    # Foreign Key to Equipment is not supported by Peewee:
    # - Equipment needs state
    # - State needs Equipment
    equipment = IntegerField(db_column='equipment_id')

    class Meta:
        database = db
        db_table = 'equipment_state'


class Station(Model):
    code = CharField()
    description = TextField()
    latitude = DecimalField(max_digits=8, decimal_places=6)
    longitude = DecimalField(max_digits=9, decimal_places=6)
    elevation = DecimalField(max_digits=5, decimal_places=1)
    state = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'network_station'


class Built(Model):
    place = ForeignKeyField(
        Place,
        db_column='place_id')
    station = ForeignKeyField(
        Station,
        db_column='station_id')

    class Meta:
        database = db
        db_table = 'network_built'


class Equipment(Model):
    model = ForeignKeyField(
        EquipmentModel,
        db_column='model_id')
    name = CharField()
    vendor = CharField()
    purchase_date = DateField()
    clock_drift = DoubleField()
    clock_drift_unit = CharField()
    storage_format = CharField()
    note = TextField()
    contact = ForeignKeyField(
        AuthUser,
        db_column='contact_id')
    owner = ForeignKeyField(
        Agency,
        db_column='owner_id')
    place = ForeignKeyField(
        Place,
        db_column='place_id')
    state = ForeignKeyField(
        State,
        db_column='state_id')
    last_edition = DateTimeField(default=datetime.now())
    last_user = ForeignKeyField(
        AuthUser,
        related_name='last_user',
        db_column='last_user_id')

    def __str__(self):
        return '%s' % self.name

    class Meta:
        database = db
        db_table = 'equipment_equipment'


class GissmoNetwork(Model):
    id = IntegerField(db_column='id')
    code = CharField(db_column='network_code')
    name = CharField(db_column='network_name')
    description = TextField()
    start = DateTimeField(db_column='start_date')
    end = DateTimeField(db_column='end_date')
    status = IntegerField(db_column='restricted_status')
    alternate_code = CharField()  # XML alternate code
    historical_code = CharField()  # XML historical code

    class Meta:
        database = db
        db_table = 'gissmo_network'


class Network(Model):
    code = CharField()
    name = CharField(null=True)
    description = TextField()
    start = DateTimeField()
    end = DateTimeField()

    class Meta:
        database = db
        db_table = 'network_network'


class GissmoBuiltType(Model):
    id = IntegerField(db_column='id')
    name = CharField(db_column='built_type_name')

    class Meta:
        database = db
        db_table = 'gissmo_builttype'


class GissmoBuilt(Model):
    id = IntegerField(db_column='id')
    station = ForeignKeyField(
        GissmoSite,
        db_column='station_id')
    _type = ForeignKeyField(
        GissmoBuiltType,
        db_column='built_type_id')
    name = CharField(db_column='built_short_desc')
    note = TextField(db_column='built_note')

    class Meta:
        database = db
        db_table = 'gissmo_built'


class GissmoDatatype(Model):
    id = IntegerField(db_column='id')
    name = CharField(db_column='type_description')

    class Meta:
        database = db
        db_table = 'gissmo_datatype'


class Datatype(Model):
    name = CharField()

    class Meta:
        database = db
        db_table = 'network_datatype'


class GissmoProject(Model):
    group = ForeignKeyField(
        AuthGroup,
        db_column='group_ptr_id')
    manager = ForeignKeyField(
        AuthUser,
        db_column='manager_id',
        null=True)

    class Meta:
        database = db
        db_table = 'gissmo_project'
        primary_key = False


class Project(Model):
    group = ForeignKeyField(
        AuthGroup,
        db_column='group_ptr_id')
    manager = ForeignKeyField(
        AuthUser,
        db_column='manager_id',
        null=True)

    class Meta:
        database = db
        db_table = 'project_project'
        primary_key = CompositeKey('group')


class GissmoChannel(Model):
    id = IntegerField(db_column='id')

    class Meta:
        database = db
        db_table = 'gissmo_channel'


class GissmoChain(Model):
    id = IntegerField(db_column='id')
    channel = ForeignKeyField(
        GissmoChannel,
        db_column='channel_id')
    order = IntegerField()
    equipment = ForeignKeyField(
        GissmoEquipment,
        db_column='equip_id')

    class Meta:
        database = db
        db_table = 'gissmo_chain'


class GissmoParameter(Model):
    id = IntegerField(db_column='id')
    name = CharField(db_column='parameter_name')
    model = ForeignKeyField(
        GissmoModel,
        db_column='equip_model_id')

    class Meta:
        database = db
        db_table = 'gissmo_parameterequip'


class GissmoValue(Model):
    id = IntegerField(db_column='id')
    parameter = ForeignKeyField(
        GissmoParameter,
        db_column='parameter_id')
    name = CharField(db_column='value')
    is_default = BooleanField(db_column='default_value')

    class Meta:
        database = db
        db_table = 'gissmo_parametervalue'


class GissmoChainConfig(Model):
    id = IntegerField(db_column='id')
    channel = ForeignKeyField(
        GissmoChannel,
        db_column='channel_id')
    chain = ForeignKeyField(
        GissmoChain,
        db_column='chain_id')
    parameter = ForeignKeyField(
        GissmoParameter,
        db_column='parameter_id')
    value = ForeignKeyField(
        GissmoValue,
        db_column='value_id')

    class Meta:
        database = db
        db_table = 'gissmo_chainconfig'


class Parameter(Model):
    name = CharField(max_length=255)
    model = ForeignKeyField(
        EquipmentModel,
        db_column='model_id')

    class Meta:
        database = db
        db_table = 'equipment_parameter'


class Value(Model):
    name = CharField(max_length=255)
    is_default = BooleanField()
    parameter = ForeignKeyField(
        Parameter,
        db_column='parameter_id')

    class Meta:
        database = db
        db_table = 'equipment_value'


class Configuration(Model):
    parameter = CharField(max_length=255)
    value = CharField(max_length=255)
    start = DateTimeField(default=datetime.now())
    end = DateTimeField()
    equipment = ForeignKeyField(
        Equipment,
        db_column='equipment_id')

    class Meta:
        database = db
        db_table = 'equipment_configuration'
