# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField

from datetime import datetime

from django.utils.timezone import make_aware

from selenium.webdriver.support.ui import Select

from gissmo.models import (
    Organism,
    EquipSupertype,
    EquipType,
    Equipment,
    EquipModel,
    Project,
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
        self.mandatory, created = Organism.objects.get_or_create(
            name='DT INSU',
            _type=0)  # to not explode equipment view (owner field)
        self.unknown, created = Organism.objects.get_or_create(
            name='Inconnu',
            _type=4)
        self.supertype_1 = EquipSupertype.objects.create(
            equip_supertype_name='01. Scientific',
            presentation_rank='1')
        self.supertype_2 = EquipSupertype.objects.create(
            equip_supertype_name='03. Telecommunication',
            presentation_rank='2')
        self.eq_type_1 = EquipType.objects.create(
            equip_supertype=self.supertype_1,
            equip_type_name='Velocimeter',
            presentation_rank='0')
        self.eq_type_2 = EquipType.objects.create(
            equip_supertype=self.supertype_2,
            equip_type_name='Router',
            presentation_rank='1')
        self.equipment_model_1 = EquipModel.objects.create(
            equip_type=self.eq_type_1,
            equip_model_name='CMG-40T')
        self.equipment_model_2 = EquipModel.objects.create(
            equip_type=self.eq_type_2,
            equip_model_name='NB1600',
            manufacturer='netmodule',
            is_network_model=True)
        self.project = Project.objects.create(
            name='ADEME',
            manager=self.superuser)
        self.superuser.groups.add(self.project)
        station_date = datetime.strptime('2015-09-27', '%Y-%m-%d')
        self.station_1 = StationSite.objects.create(
            # TODO: add new ActorType model
            site_type=StationSite.OBSERVATOIRE,
            station_code='EOST',
            operator=self.unknown,
            creation_date=make_aware(station_date),  # make it aware
            project=self.project,
            actor=self.superuser)

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
        purchase_date = datetime.strptime('2015-10-01', '%Y-%m-%d')
        self.equipment_1 = Equipment.objects.create(
            equip_model=self.equipment_model_1,
            serial_number='T4Q31',
            owner=self.mandatory,
            stockage_site=self.station_1,
            purchase_date=make_aware(purchase_date),
            actor=self.superuser)

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

    def test_equipment_network_config(self):
        # @EOST, after an installation of a given equipment (NB1600 model),
        # we need to fill in IP Addresses and services
        purchase_date = datetime.strptime('2016-01-18', '%Y-%m-%d')
        self.equipment_1 = Equipment.objects.create(
            equip_model=self.equipment_model_2,
            serial_number='00112B00153',
            owner=self.mandatory,
            purchase_date=make_aware(purchase_date),
            stockage_site=self.station_1,
            actor=self.superuser)

        # After some times, we need to use this equipment.
        # We configure it and add 2 IP Addresses and 1 service
        ip = InputField(
            name='ipaddress_set-0-ip',
            content='192.168.0.100')
        netmask = InputField(
            name='ipaddress_set-0-netmask',
            content='255.255.255.0')
        ip2 = InputField(
            name='ipaddress_set-1-ip',
            content='station.dyndns.tld')
        netmask2 = InputField(
            name='ipaddress_set-1-netmask',
            content='0.0.0.0')
        protocol = InputField(
            name='service_set-0-protocol',
            content='Seed link protocol',
            _type=Select)
        port = InputField(
            name='service_set-0-port',
            content='18000')

        click_paths = ['//a[. = "Add another Ip address"]']

        fields = [ip, netmask, protocol, port, ip2, netmask2]

        url = '%sequipment/%s' % (self.appurl, self.equipment_1.id)
        self.fill_in_form(url, fields, click_paths)
