# -*- coding: utf-8 -*-
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from django.contrib.auth.models import User
from gissmo.models import Project


class ProjectTest(FunctionalTest):

    def setUp(self):
        """
        Add user in order to test project creation with another user than admin.
        """
        super(ProjectTest, self).setUp()
        self.user_1 = User.objects.create_user(
            'john',
            'john@mysite.com',
            'doe')

    def test_project_creation(self):
        """
        Check a simple Project creation
        """
        # As each station should be into a project we need to create one.
        name = InputField(
            name='project_name',
            content='ADEME',
            check=True)
        manager = InputField(
            name='manager',
            content='john',
            _type=Select)

        fields = [name, manager]

        self.add_item_in_admin_and_check_presence_in_list(
            'project/',
            fields)

    def test_project_user_creation(self):
        """
        Check that we can create a project user.
        """
        # Even if John is the ADEME project manager, we need to add him to the
        # project so that it can create some sites (Stationsite).
        self.project_1 = Project.objects.create(
            project_name='ADEME',
            manager=self.user_1)
        self.project_2 = Project.objects.create(
            project_name='G-EAU-THERMIE',
            manager=self.user_1)

        user = InputField(
            name='user',
            content='john',
            check=True)
        project = InputField(
            name='project',
            content=self.project_1.id,
            _type='checkbox')

        fields = [user, project]

        self.add_item_in_admin_and_check_presence_in_list(
            'projectuser/',
            fields)
