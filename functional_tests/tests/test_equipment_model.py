# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField

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
        self.supertype_2 = EquipSupertype.objects.create(
            equip_supertype_name='03. Telecommunication',
            presentation_rank='2')
        self.eq_type2 = EquipType.objects.create(
            equip_supertype=self.supertype_2,
            equip_type_name='Router',
            presentation_rank='1')

    def test_equipment_model_creation(self):
        """
        Check a simple Equipment Model creation
        """
        # @EOST we often receive CMG-40T equipment. They are Scientific
        # velocimeters.
        # We check that CMG-40T appears in the given Equipment Model list
        _type = InputField(
            name='equip_type',
            content='Velocimeter',
            _type='autocomplete')
        name = InputField(
            name='equip_model_name',
            content='CMG-40T',
            check=True)
        manufacturer = InputField(
            name='manufacturer',
            content='Güralp')

        fields = [_type, name, manufacturer]

        self.add_item_in_admin('equipmodel/', fields, check=True)

    def test_equipment_network_model_creation(self):
        """
        Check that we can use the checkbox to activate Network area for
        equipments linked to this Equipment Model
        """
        # @EOST we receive a new router equipment. It needs to be configured
        # with IP Address. We so add a new Equipment model with
        # "is_network_model" field checked.
        _type = InputField(
            name='equip_type',
            content='Router',
            _type='autocomplete')
        name = InputField(
            name='equip_model_name',
            content='NB1600',
            check=True)
        manufacturer = InputField(
            name='manufacturer',
            content='netmodule')
        is_network_model = InputField(
            name='is_network_model',
            content=[True],
            _type='checkbox')

        fields = [_type, name, manufacturer, is_network_model]

        self.add_item_in_admin('equipmodel/', fields, check=True)
