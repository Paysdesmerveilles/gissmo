# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import Organism


class OrganismTest(FunctionalTest):

    def get_type_choice_name(self, number):
        res = ''
        if not number or number > 7:
            return res
        for element in Organism.ORGANISM_TYPE_CHOICES:
            if element[0] == number:
                res = element[1]
                break
        return res

    def test_organism_creation(self):
        """
        Check a simple organism creation
        """
        # @EOST we have a group called: "EOST".
        # We enter it in the system and check we are redirect to its list.
        # Then we check that it appears in the given organism list.
        _type = InputField(
            name='_type',
            content=self.get_type_choice_name(Organism.UNKNOWN),
            _type=Select)
        name = InputField(
            name='name',
            content='EOST',
            check=True)

        fields = [_type, name]

        self.add_item_in_admin('organism/', fields, check=True)
