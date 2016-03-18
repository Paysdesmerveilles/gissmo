# -*- coding: utf-8 -*-
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import (
    Affiliation,
    Project,
    StationSite
)


class StationSiteTest(FunctionalTest):

    def setUp(self):
        super(StationSiteTest, self).setUp()
        # This site view need by default an unknown affiliation
        self.mandatory, created = Affiliation.objects.get_or_create(
            name='DT INSU',
            _type=0)  # to not explode equipment view (owner field)
        self.unknown, created = Affiliation.objects.get_or_create(
            name='Inconnu',
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
