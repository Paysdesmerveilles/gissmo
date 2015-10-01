# -*- coding: utf-8 -*-
from .base import FunctionalTest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


class ActorTest(FunctionalTest):

    def test_actor_creation(self):
        """
        Check a simple actor creation
        """
        # @EOST a new protagonist comes. His name is: John Doe.
        # We enter him in the system and check we are redirect to actor list
        actor_expected_name = 'John DOE'
        self.gissmo_login()
        url = self.appurl + 'actor/add'
        self.browser.get(url)

        input_actortype = Select(self.browser.find_element_by_name('actor_type'))
        input_actortype.select_by_value('6')
        input_name = self.browser.find_element_by_name('actor_name')
        input_name.send_keys(actor_expected_name)
        input_name.send_keys(Keys.ENTER)

        self.assertEqual(self.browser.current_url, self.appurl + 'actor/')

        # We check that John Doe appears in the given actor list
        table = self.browser.find_element_by_id('result_list')
        rows = table.find_elements_by_xpath('//tbody/tr//th')
        self.assertIn(actor_expected_name, [row.text for row in rows])
