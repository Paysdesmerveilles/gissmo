# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import EquipSupertype


class EquipmentTypeTest(FunctionalTest):

    def setUp(self):
        """
        Some needed datas
        """
        super(EquipmentTypeTest, self).setUp()
        self.supertype_1 = EquipSupertype.objects.create(
            equip_supertype_name='01. Scientific',
            presentation_rank='1')
        self.supertype_2 = EquipSupertype.objects.create(
            equip_supertype_name='02. Energetic',
            presentation_rank='2')

    def test_equipment_type_creation(self):
        """
        Check a simple Equipment Type creation
        """
        # For starting purposes, we need to define some Equipment types,
        # as Solar panel. So we create a new Solar Panel (Energetic SuperType)
        # We check that Solar Panel appears in the given Equipment type list
        supertype = InputField(
            name='equip_supertype',
            content='02. Energetic',
            _type=Select)
        _type = InputField(
            name='equip_type_name',
            content='Solar panel',
            check=True)
        rank = InputField(
            name='presentation_rank',
            content='0')

        fields = [supertype, _type, rank]

        self.add_item_in_admin('equiptype/', fields, check=True)
