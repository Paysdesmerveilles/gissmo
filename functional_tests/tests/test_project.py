# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from django.contrib.auth.models import User


class ProjectTest(FunctionalTest):

    def setUp(self):
        """
        Add user in order to test project creation with another user than
        admin.
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
            name='name',
            content='ADEME',
            check=True)
        manager = InputField(
            name='manager',
            content='john',
            _type=Select)

        fields = [name, manager]

        self.add_item_in_admin('project/', fields, check=True)
