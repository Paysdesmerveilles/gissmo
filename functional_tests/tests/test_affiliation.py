# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import Affiliation


class AffiliationTest(FunctionalTest):

    def get_type_choice_name(self, number):
        res = ''
        if not number or number > 7:
            return res
        for element in Affiliation.AFFILIATION_TYPE_CHOICES:
            if element[0] == number:
                res = element[1]
                break
        return res

    def test_affiliation_creation(self):
        """
        Check a simple affiliation creation
        """
        # @EOST we have a group called: "EOST".
        # We enter it in the system and check we are redirect to its list.
        # Then we check that it appears in the given affiliation list.
        _type = InputField(
            name='_type',
            content=self.get_type_choice_name(Affiliation.UNKNOWN),
            _type=Select)
        name = InputField(
            name='name',
            content='EOST',
            check=True)

        fields = [_type, name]

        self.add_item_in_admin('affiliation/', fields, check=True)
