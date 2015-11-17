# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from selenium.webdriver.common.keys import Keys


class CheckMainURLBehaviourTest(FunctionalTest):

    def test_can_get_main_pages(self):
        """
        Check that each page don't send a 404 error message
        """
        # Martin Dupont start using the site by accessing to /gissmo after
        # the webpage URL
        url = self.adminurl
        self.browser.get(url)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn(
            'Gissmo', header_text,
            'Problem loading %s' % self.browser.current_url)

        # He puts his username and password to connect the admin interface
        self.assertIn(
            'Log in', self.browser.title,
            'Problem loading %s: Not login page' % self.browser.current_url)
        inputlogin = self.browser.find_element_by_id('id_username')
        inputpassword = self.browser.find_element_by_id('id_password')
        inputlogin.send_keys(self.DEFAULT_ADMIN_LOGIN)
        inputpassword.send_keys(self.DEFAULT_ADMIN_PASSWORD)

        # When he hits enter, the page updates, and now administration appears
        inputpassword.send_keys(Keys.ENTER)
        self.assertIn(
            'Site administration',
            self.browser.title,
            'Login problem on %s: no administration interface found.')

        # As Martin don't know how the website works he will browse it
        # So it checks some links
        links_to_check = [
            'stationsite/',
            'equipmodel/',
            'equipment/',
            'intervention/',
            'actor/',
            'network/',
            'project/',
            'equipmodeldoctype/',
            'equipdoctype/',
            'projectuser/',
            'stationdoctype/',
            'builttype/',
            'equiptype/',
            'calibrationunit/',
            'datatype/',
            'parameterequip/',
            'parametervalue/',
            'channel/',
            'channelcode/'
        ]
        for code in links_to_check:
            url = self.appurl + code
            self.browser.get(url)
            self.assertNotIn(
                'Page not found',
                self.browser.title,
                "Not found URL: %s" % self.browser.current_url)
            self.assertIn(
                'Select',
                self.browser.title,
                "No 'select' on title. %s" % self.browser.current_url)
            self.assertIn(
                'to change',
                self.browser.title,
                "No 'to change' on title. %s" % self.browser.current_url)
