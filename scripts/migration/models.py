import os

from peewee import (
    BooleanField,
    CharField,
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
PORT = os.getenv('DB_PORT_5432_TCP_PORT', '5432')

db = PooledPostgresqlExtDatabase(
    DB,
    max_connections=32,
    stale_timeout=300,
    user=USER,
    password=PWD,
    host=HOST,
    port=PORT,
    register_hstore=False)


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

organism_choices = (
    (0, 'Observatory/Laboratory'),
    (1, 'Network'),
    (2, 'Business'),
    (3, 'Customer service company'),
    (4, 'Unknown'),
)


class GissmoOrganism(Model):
    id = IntegerField(db_column='id')
    name = CharField()
    _type = IntegerField(choices=organism_choices)
    parent = ForeignKeyField(
        'self',
        null=True,
        db_column='parent_id')

    class Meta:
        database = db
        db_table = 'gissmo_organism'


class Organism(Model):
    name = CharField()
    _type = IntegerField(choices=organism_choices)
    parent = ForeignKeyField(
        'self',
        null=True,
        db_column='parent_id')

    def __str__(self):
        return '%s' % self.name

    class Meta:
        database = db
        db_table = 'affiliation_organism'


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
    operator = ForeignKeyField(Organism, db_column='operator_id')
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
    (1, 'Agency'),
    (2, 'Theoritical site'),
    (3, 'Measuring site'),
    (4, 'Customer service place'),
    (5, 'Tunnel'),
    (6, 'Drift'),
    (7, 'Drain'),
    (8, 'Cave'),
    (9, 'Underground'),
    (10, 'Cabinet'),
    (11, 'Chamber'),
    (12, 'Prefabricated'),
    (13, 'Premises'),
    (14, 'Fort'),
    (15, 'Apron'),
    (16, 'Slab'),
    (17, 'Outside'),
    (18, 'Well'),
    (19, 'Drilling'),
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
    operator = ForeignKeyField(Organism, db_column='operator_id')
    parent = ForeignKeyField('self', db_column='parent_id')

    class Meta:
        database = db
        db_table = 'place_place'


class AuthUser(Model):
    id = IntegerField(db_column='id')

    class Meta:
        database = db
        db_table = 'auth_user'


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
    # xml_restricted_status is never filled in
    # same thing for xml_historical_code
    xml_alternate_code = CharField()
    operator = ForeignKeyField(
        Organism,
        db_column='operator_id')
    place = ForeignKeyField(
        Place,
        db_column='place_id')
    state = ForeignKeyField(
        State,
        db_column='state_id')

    class Meta:
        database = db
        db_table = 'network_station'


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
        Organism,
        db_column='owner_id')
    place = ForeignKeyField(
        Place,
        db_column='place_id')
    state = ForeignKeyField(
        State,
        db_column='state_id')

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
    xml_historical_code = CharField()
    xml_alternate_code = CharField()
    xml_restricted_status = IntegerField()

    class Meta:
        database = db
        db_table = 'network_network'
