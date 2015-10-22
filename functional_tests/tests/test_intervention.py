# -*- coding: utf-8 -*-
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import (
    Actor,
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
        self.station_1 = StationSite.objects.create(
            site_type=StationSite.OBSERVATOIRE,
            station_code='EOST',
            operator=self.unknown_actor)

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
