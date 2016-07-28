# -*- coding: utf-8 -*-
from .base import FunctionalTest
from .input_field import InputField

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from gissmo.models import (
    BuiltType,
    Organism,
    Project,
    StationSite
)

from time import sleep
from datetime import datetime


class StationSiteTest(FunctionalTest):

    def setUp(self):
        super(StationSiteTest, self).setUp()
        # This site view need by default an unknown organism
        self.mandatory, created = Organism.objects.get_or_create(
            name='DT INSU',
            _type=0)  # to not explode equipment view (owner field)
        self.unknown, created = Organism.objects.get_or_create(
            name='Unknown',
            _type=4)
        self.project = Project.objects.create(
            name='ADEME',
            manager=self.superuser)
        self.superuser.groups.add(self.project)

    def get_site_choice_name(self, number):
        res = ''
        if not number or number > 7:
            return res
        for element in StationSite.SITE_CHOICES:
            if element[0] == number:
                res = element[1]
                break
        return res

    def test_stationsite_creation(self):
        """
        Check a simple Site creation
        """
        # Hey guys, we forget to create the EOST place!
        observatory = self.get_site_choice_name(StationSite.OBSERVATOIRE)
        site_type = InputField(
            name='site_type',
            content=observatory,
            _type=Select)
        code = InputField(
            name='station_code',
            content='EOST',
            check=True)
        project = InputField(
            name='project',
            content='ADEME',
            _type=Select)
        date = InputField(
            name='creation_date',
            content='2015-10-04')

        fields = [site_type, code, project, date]

        self.add_item_in_admin(
            'stationsite/',
            fields,
            check=True)

    def test_stationsite_creation_with_new_place(self):
        """
        Check that we can add EC9 Soil Classification on a place.
        """
        # Initialisation
        BuiltType.objects.create(
            built_type_name='Local')
        station_date = datetime.strptime('2016-07-28', '%Y-%m-%d')
        site = StationSite.objects.create(
            site_type=StationSite.OBSERVATOIRE,
            station_code='EOST',
            operator=self.unknown,
            creation_date=station_date,
            project=self.project,
            actor=self.superuser)

        # Add new build on EOST site
        self.gissmo_login()
        url = self.appurl + 'stationsite/%s' % site.id
        self.browser.get(url)

        link = self.browser.find_element_by_link_text('Add another Place')
        link.click()
        self.browser.implicitly_wait(3)

        storage_description = 'Storage area'
        _type = InputField(
            name='built_set-0-built_type',
            content='Local',
            _type=Select)
        name = InputField(
            name='built_set-0-built_short_desc',
            content=storage_description)
        soil = InputField(
            name='built_set-0-ground_type',
            content='A',
            _type=Select)

        fields = [_type, name, soil]
        for field in fields:
            self.fill_in_field(field)

        input_save = self.browser.find_element_by_name('_save')
        input_save.send_keys(Keys.ENTER)
        self.browser.implicitly_wait(3)

        # Check EOST site that new build was saved
        self.browser.get(url)
        sleep(1)
        bsd = self.browser.find_element_by_name('built_set-0-built_short_desc')
        desc = bsd.get_attribute('value')
        self.assertEqual(
            desc,
            storage_description,
            '%s description expected. Current: %s' % (
                storage_description, desc))
        bgt = Select(self.browser.find_element_by_name(
            'built_set-0-ground_type'))
        groundtype = bgt.first_selected_option.text
        self.assertEqual(
            groundtype,
            'A',
            '%s ground type expected. Current: %s' % ('A', bgt))
