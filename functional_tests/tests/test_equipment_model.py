# -*- coding: utf-8 -*-
from .base import FunctionalTest
from .input_field import InputField
from selenium.webdriver.support.ui import Select

from gissmo.models import (
    EquipSupertype,
    EquipType)


class EquipmentModelTest(FunctionalTest):

    def setUp(self):
        """
        Some needed datas
        """
        super(EquipmentModelTest, self).setUp()
        self.supertype_1 = EquipSupertype.objects.create(
            equip_supertype_name='01. Scientific',
            presentation_rank='1')
        self.eq_type = EquipType.objects.create(
            equip_supertype=self.supertype_1,
            equip_type_name='Velocimeter',
            presentation_rank=0)

    def test_equipment_model_creation(self):
        """
        Check a simple Equipment Model creation
        """
        # @EOST we often receive CMG-40T equipment. They are Scientific
        # velocimeters.
        # We check that CMG-40T appears in the given Equipment Model list
        supertype = InputField(
            name='equip_supertype',
            content='01. Scientific',
            _type=Select)
        _type = InputField(
            name='equip_type',
            content='Velocimeter',
            _type=Select)
        name = InputField(
            name='equip_model_name',
            content='CMG-40T',
            check=True)
        manufacturer = InputField(
            name='manufacturer',
            content=u'Güralp')

        fields = [supertype, _type, name, manufacturer]

        self.add_item_in_admin_and_check_presence_in_list('equipmodel/', fields)
