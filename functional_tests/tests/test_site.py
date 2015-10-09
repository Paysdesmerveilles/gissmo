# -*- coding: utf-8 -*-
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import (
    Actor,
    Project,
    ProjectUser)


class StationSiteTest(FunctionalTest):

    def setUp(self):
        super(StationSiteTest, self).setUp()
        # This site view need by default an unknown actor and an actor that have
        # the same name of username
        self.superuser_actor = Actor.objects.create(
            actor_name=self.superuser.username,
            actor_type=7)
        self.project = Project.objects.create(
            project_name='ADEME',
            manager=self.superuser)
        self.projectuser = ProjectUser.objects.create(
            user=self.superuser)
        # Link last ProjectUser to ADEME
        self.projectuser.project.add(self.project)

    def test_stationsite_creation(self):
        """
        Check a simple Site creation
        """
        # Hey guys, we forget to create the EOST place!
        site_type = InputField(
            name='site_type',
            content='Observatoire',
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
