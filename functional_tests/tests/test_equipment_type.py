# -*- coding: utf-8 -*-
from .base import FunctionalTest
from selenium.webdriver.common.keys import Keys
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
        self.gissmo_login()
        url = self.appurl + 'equiptype/add'
        expected_value = 'Solar panel'
        self.browser.get(url)

        input_type = Select(self.browser.find_element_by_name('equip_supertype'))
        input_type.select_by_value('2')
        input_name = self.browser.find_element_by_name('equip_type_name')
        input_name.send_keys(expected_value)
        input_rank = self.browser.find_element_by_name('presentation_rank')
        input_rank.send_keys('0')
        input_rank.send_keys(Keys.ENTER)

        self.assertEqual(self.browser.current_url, self.appurl + 'equiptype/')

        # We check that Solar Panel appears in the given Equipment type list
        table = self.browser.find_element_by_id('result_list')
        rows = table.find_elements_by_xpath('//tbody/tr//th')
        self.assertIn(expected_value, [row.text for row in rows])
