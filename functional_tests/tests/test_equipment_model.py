# -*- coding: utf-8 -*-
from .base import FunctionalTest
from selenium.webdriver.common.keys import Keys
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
        self.gissmo_login()
        url = self.appurl + 'equipmodel/add'
        expected_value = 'CMG-40T'
        self.browser.get(url)

        input_supertype = Select(self.browser.find_element_by_name('equip_supertype'))
        input_supertype.select_by_visible_text('01. Scientific')
        input_type = Select(self.browser.find_element_by_name('equip_type'))
        input_type.select_by_visible_text('Velocimeter')
        input_name = self.browser.find_element_by_name('equip_model_name')
        input_name.send_keys(expected_value)
        input_manufacturer = self.browser.find_element_by_name('manufacturer')
        input_manufacturer.send_keys(u'Güralp')
        input_manufacturer.send_keys(Keys.ENTER)

        self.assertEqual(self.browser.current_url, self.appurl + 'equipmodel/')

        # We check that CMG-40T appears in the given Equipment Model list
        table = self.browser.find_element_by_id('result_list')
        rows = table.find_elements_by_xpath('//tbody/tr//th')
        self.assertIn(expected_value, [row.text for row in rows])
