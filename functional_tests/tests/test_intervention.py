# -*- coding: utf-8 -*-
from .base import FunctionalTest
from .input_field import InputField

from time import sleep
from datetime import datetime

from django.utils.timezone import make_aware

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from gissmo.models import (
    Actor,
    Equipment,
    EquipType,
    EquipSupertype,
    EquipModel,
    Project,
    ProjectUser,
    StationSite)


class InterventionTest(FunctionalTest):

    def setUp(self):
        """
        Some needed datas
        """
        super(InterventionTest, self).setUp()
        self.unknown_actor, created = Actor.objects.get_or_create(
            actor_name='Inconnu',
            actor_type=6)
        self.superuser_actor = Actor.objects.create(
            actor_name=self.superuser.username,
            actor_type=7)
        self.project = Project.objects.create(
            project_name='ADEME',
            manager=self.superuser)
        self.projectuser = ProjectUser.objects.create(
            user=self.superuser)
        self.projectuser.project.add(self.project)
        station_date = datetime.strptime('2015-09-26', '%Y-%m-%d')
        self.station_1 = StationSite.objects.create(
            site_type=StationSite.OBSERVATOIRE,
            station_code='EOST',
            operator=self.unknown_actor,
            creation_date=make_aware(station_date),
            project=self.project,
            actor=self.superuser)

    def test_nochanges_default_actor_intervention_creation(self):
        """
        Check a simple Intervention creation
        """
        # After having upgraded to Django 1.8, Maxime encounts a problem
        # validating the Intervention Form with default Actor value: himself.
        # He so check on Intervention Form on which no default Actor is
        # selected that the object is well written.
        station = InputField(
            name='station',
            content='EOST',
            _type=Select)
        date = InputField(
            name='intervention_date_0',
            content='2015-10-06')

        fields = [station, date]

        self.add_item_in_admin('intervention/', fields, check=False)
        self.browser.implicitly_wait(3)

        # Check manually presence in list as the Intervention creation doesn't
        # redirect to intervention list
        url = self.appurl + 'intervention/'
        self.browser.get(url)
        self.check_presence_in_list('intervention/', [station])

    def test_add_new_intervention_while_testing_new_equipment(self):
        """
        While testing a new equipment, we create a new intervention
        """
        # During Python3 migration, select fields on an equipment didn't work.
        # This is because of __unicode__() that becomes __str__() in Python3.
        # We so test that it's possible via the web interface to create
        # an intervention with an equipment.

        # Initialisation
        self.mandatory_actor, created = Actor.objects.get_or_create(
            actor_name='DT INSU',
            actor_type=1)
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
        # Prepare equipment
        self.equipment_1 = Equipment.objects.create(
            equip_model=self.equipment_model,
            serial_number='T4Q31',
            owner=self.mandatory_actor,
            stockage_site=self.station_1,
            purchase_date='2015-10-29',
            actor=self.superuser_actor)

        # Maxime login to the application in order to add an intervention
        self.gissmo_login()
        url = self.appurl + 'intervention/add'
        self.browser.get(url)
        # First he adds another intervention equipment
        link = self.browser.find_element_by_xpath('//a[. = "Add another Interv equip"]')
        link.click()
        self.browser.implicitly_wait(3)
        station = InputField(
            name='station',
            content='EOST',
            _type=Select)
        date = InputField(
            name='intervention_date_0',
            content='2015-11-01')
        intervention_name = InputField(
            name='intervequip_set-0-equip_action',
            content='Tester',
            _type=Select)

        fields = [
            station,
            date,
            intervention_name]

        # He fill in first fields and then add "Tester" in Interv Equip action
        for field in fields:
            self.fill_in_field(field)

        # For right equipment to appear, we use tabulation key
        testing_input = self.browser.find_element_by_name('intervequip_set-0-equip_action')
        testing_input.send_keys(Keys.TAB)

        # Then he choose its equipment and set it to disponible
        equipment = InputField(
            name='intervequip_set-0-equip',
            content=str(self.equipment_1),
            _type=Select)
        self.fill_in_field(equipment)
        state = InputField(
            name='intervequip_set-0-equip_state',
            content='Disponible',
            _type=Select)
        self.fill_in_field(state)

        # Save form
        sleep(3)
        input_save = self.browser.find_element_by_name('_save')
        input_save.send_keys(Keys.ENTER)
