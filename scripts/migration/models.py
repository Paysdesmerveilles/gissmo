import os

from peewee import (
    BooleanField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
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

    class Meta:
        database = db
        db_table = 'affiliation_organism'
