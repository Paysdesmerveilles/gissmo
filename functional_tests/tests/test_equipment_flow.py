# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import (
    Actor,
    EquipSupertype,
    EquipType,
    Equipment,
    EquipModel,
    Project,
    ProjectUser,
    StationSite)


class EquipmentTest(FunctionalTest):

    def setUp(self):
        """
        Initialize some needed data:
          - Actors
          - SuperType of Equipment
          - Equipment Type
        """
        super(EquipmentTest, self).setUp()
        # TODO: Delete dependancy from this 2 actors if possible.
        self.mandatory_actor, created = Actor.objects.get_or_create(
            actor_name='DT INSU',
            actor_type=1)  # to not explode equipment view (owner field)
        self.unknown_actor, created = Actor.objects.get_or_create(
            actor_name='Inconnu',
            actor_type=6)
        self.superuser_actor = Actor.objects.create(
            actor_name=self.superuser.username,
            actor_type=7)
        self.supertype_1 = EquipSupertype.objects.create(
            equip_supertype_name='01. Scientific',
            presentation_rank='1')
        self.eq_type = EquipType.objects.create(
            equip_supertype=self.supertype_1,
            equip_type_name='Velocimeter',
            presentation_rank=0)
        self.equipment_model = EquipModel.objects.create(
            equip_type=self.eq_type,
            equip_model_name='CMG-40T')
        self.project = Project.objects.create(
            project_name='ADEME',
            manager=self.superuser)
        self.projectuser = ProjectUser.objects.create(
            user=self.superuser)
        self.projectuser.project.add(self.project.id)
        self.station_1 = StationSite.objects.create(
            # TODO: add new ActorType model
            site_type=StationSite.OBSERVATOIRE,
            station_code='EOST',
            operator=self.unknown_actor)
        self.project.station.add(self.station_1.id)

    def test_equipment_creation(self):
        """
        Check a simple equipment creation
        """
        # @EOST we receive a new CMG-40T equipment: T4Q30
        model = InputField(
            name='equip_model',
            content='CMG-40T',
            _type='autocomplete')
        serial = InputField(
            name='serial_number',
            content='T4Q30',
            check=True)
        owner = InputField(
            name='owner',
            content='DT INSU',
            _type=Select)
        date = InputField(
            name='purchase_date',
            content='2015-10-04')
        site = InputField(
            name='stockage_site',
            content='EOST',
            _type=Select)

        fields = [model, serial, owner, date, site]

        self.add_item_in_admin('equipment/', fields, check=True)

    def test_equipment_installation_on_a_site(self):
        # @EOST we receive a new equipment CMG-40T: T4Q31
        self.equipment_1 = Equipment.objects.create(
            equip_model=self.equipment_model,
            serial_number='T4Q31',
            owner=self.mandatory_actor,
            stockage_site=self.station_1,
            purchase_date='2015-10-01',
            actor=self.superuser_actor.actor_name)

        # We test it in stockage place.
        # It becomes so available.
        station = InputField(
            name='station',
            content='EOST',
            _type=Select)
        intervention_date_0 = InputField(
            name='intervention_date_0',
            content='2015-10-04',
            check=True)
        intervention_date_1 = InputField(
            name='intervention_date_1',
            content='11:14:00',
            check=True)
        intervenant = InputField(
            name='intervactor_set-0-actor',
            content=self.superuser.username,
            _type=Select)

        fields = [
            station,
            intervention_date_0,
            intervention_date_1,
            intervenant,
        ]

        # self.add_item_in_admin('intervention/', fields, check=False)

        # We install it on a new site with a assembly (bâti).
        # We add channel HHE, 100Mhz frequency

        # 3 weeks after, we decide to finish to test the site. Uninstall the
        # equipement for test. We define channels as finished.

        # We test the equipment and so we put it in another place.
