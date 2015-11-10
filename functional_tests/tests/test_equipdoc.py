# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from gissmo.models import (
    Actor,
    EquipDocType,
    EquipModel,
    EquipSupertype,
    EquipType,
    Project,
    ProjectUser,
    StationSite)
from gissmo.settings.common import UPLOAD_ROOT

from datetime import datetime
from time import sleep
import os

from django.utils.timezone import make_aware

UPLOADED_FILE = 'equipdoc_cmg40t_manual.txt'


class EquipDocTest(FunctionalTest):

    def setUp(self):
        """
        Initialize some needed data:
          - Actors
          - SuperType of Equipment
          - Equipment Type
        """
        super(EquipDocTest, self).setUp()
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
        station_date = datetime.strptime('2015-09-27', '%Y-%m-%d')
        self.station_1 = StationSite.objects.create(
            # TODO: add new ActorType model
            site_type=StationSite.OBSERVATOIRE,
            station_code='EOST',
            operator=self.unknown_actor,
            creation_date=make_aware(station_date),  # make it aware
            project=self.project,
            actor=self.superuser)
        self.project.station.add(self.station_1.id)
        self.equipdoctype_1 = EquipDocType.objects.create(
            equipdoc_type_name='Pictures')
        self.equipdoctype_2 = EquipDocType.objects.create(
            equipdoc_type_name='Management report')
        self.equipdoctype_3 = EquipDocType.objects.create(
            equipdoc_type_name='Other')

    def tearDown(self):
        """
        Clean document uploaded by tests
        """
        # clean working directory
        for root, dirs, files in os.walk(UPLOAD_ROOT, topdown=False):
            for name in files:
                if name == UPLOADED_FILE:
                    os.remove(os.path.join(root, name))

    def test_document_upload(self):
        """
        Test that we can send a file to Gissmo.
        """
        # @EOST we receive a new CMG-40T, T4Q32 (serial_number) supplied with
        # a TXT document that explains how it works.
        # We so create the new appliance with an attachment: the document

        model = InputField(
            name='equip_model',
            content='CMG-40T',
            _type='autocomplete')
        serial = InputField(
            name='serial_number',
            content='T4Q32',
            check=True)
        owner = InputField(
            name='owner',
            content='DT INSU',
            _type=Select)
        date = InputField(
            name='purchase_date',
            content='2015-11-06')
        site = InputField(
            name='stockage_site',
            content='EOST',
            _type=Select)

        fields = [model, serial, owner, date, site]

        # We so log in, go to equipment, add a new one
        self.gissmo_login()
        url = self.appurl + 'equipment/add'
        self.browser.get(url)

        for field in fields:
            self.fill_in_field(field)

        # We add a new Equipment Document area to input a new document
        link = self.browser.find_element_by_xpath("//a[. = \"Add another Document de l'equipement\"]")
        link.click()
        self.browser.implicitly_wait(3)

        # We add a new management report about CMG40-T working
        _type = InputField(
            name='equipdoc_set-0-document_type',
            content='Management report',
            _type=Select)
        title = InputField(
            name='equipdoc_set-0-document_title',
            content='CMG-40T Official Manual')
        file_path = os.path.join(os.getcwd(), 'functional_tests/tests/data/%s' % UPLOADED_FILE)
        self.assertTrue(os.path.exists(file_path))
        _file = InputField(
            name='equipdoc_set-0-document_equip',
            content=file_path)
        fields = [_type, title, _file]
        for field in fields:
            self.fill_in_field(field)

        # Finally we validate the form
        sleep(3)  # waiting for developer to see if problem occurs
        input_save = self.browser.find_element_by_name('_save')
        input_save.send_keys(Keys.ENTER)
        self.browser.implicitly_wait(3)

        # Check directory content
        is_present = False
        for root, dirs, files in os.walk(UPLOAD_ROOT, topdown=False):
            for name in files:
                if name == UPLOADED_FILE:
                    is_present = True
        self.assertTrue(is_present, "File not found in upload directory.")
