# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField


class EquipDocTypeTest(FunctionalTest):

    def test_equipdoctype_creation(self):
        """
        Check that we can add some type of document (Equipment)
        """
        # @EOST we're used to add Management report document to equipment.
        # We so login to the system, go to Type of document(equipment) menu
        # and add a new "Management report" type.
        _type = InputField(
            name='equipdoc_type_name',
            content='Management report',
            check=True)

        self.add_item_in_admin('equipdoctype/', [_type], check=True)
