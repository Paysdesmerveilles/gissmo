# -*- coding: utf-8 -*-
from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import \
#        DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import unittest
import os
import csv
import sys

from django.test import LiveServerTestCase
from django.contrib.auth.models import User

DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'
DOWNLOAD_PATH = os.getcwd()
DOWNLOADED_FILE = 'test_site.csv'


class SimpleTest(LiveServerTestCase):
    """
    A set of tests that only load some webpages from Gissmo.
    """

    def setUp(self):
        """
        Launch Firefox as Web Testing Platform.
        """
        self.superuser = User.objects.create_superuser(
            DEFAULT_ADMIN_LOGIN,
            'admin@mysite.com',
            DEFAULT_ADMIN_PASSWORD)
        # Set Firefox profile to DL CSV files
        fp = webdriver.FirefoxProfile()

        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", DOWNLOAD_PATH)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

#        # Create a connection to a Remote Selenium Node
#        self.browser = webdriver.Remote(
#            command_executor='http://selenium:4444/wd/hub',
#            desired_capabilities=DesiredCapabilities.FIREFOX,
#            browser_profile=fp,
#        )

        self.browser = webdriver.Firefox(firefox_profile=fp)
        self.browser.implicitly_wait(3)

        self.url = self.live_server_url + '/'
        self.adminurl = self.url + 'gissmo/'
        self.appurl = self.adminurl + 'gissmo/'

    def tearDown(self):
        """
        Cleaning
        """
        # close firefox
        self.browser.quit()

        # Bug: https://code.djangoproject.com/ticket/10827
        from django.contrib.contenttypes.models import ContentType
        ContentType.objects.clear_cache()

        # clean working directory
        csv_filename = DOWNLOADED_FILE
        filepath = '/'.join([DOWNLOAD_PATH, csv_filename])
        if os.path.exists(filepath):
            os.remove(filepath)

    def gissmo_login(self):
        """
        Log in to Gissmo application.
        """
        url = self.adminurl
        self.browser.get(url)
        inputlogin = self.browser.find_element_by_name('username')
        inputpassword = self.browser.find_element_by_name('password')
        inputlogin.send_keys(DEFAULT_ADMIN_LOGIN)
        inputpassword.send_keys(DEFAULT_ADMIN_PASSWORD)
        inputpassword.send_keys(Keys.ENTER)

        self.browser.implicitly_wait(3)
        # Stop tests if login failed
        self.assertIn(
            'Site administration',
            self.browser.title,
            'Login problem on %s: no administration interface found.')

    def check_csv_file(self, filepath):
        """
        Browse the given CSV file to check if any error occured.
        """
        with open(filepath, 'rb') as f:
            reader = csv.reader(f)
            try:
                # just browse rows
                for row in reader:
                    pass
            except csv.Error as e:
                sys.exit(
                    'file %s, line %d: %s' %
                    (filepath, reader.line_num, e))

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
        inputlogin.send_keys(DEFAULT_ADMIN_LOGIN)
        inputpassword.send_keys(DEFAULT_ADMIN_PASSWORD)

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

    def test_station_map_loading(self):
        """
        Check that Station Map is visible.
        """
        # Yvette wants to check Station Map.
        # She log in to Gissmo.
        self.gissmo_login()

        # Then she goes to Site List to check the Station Map link
        url = self.appurl + 'stationsite/'
        self.browser.get(url)
        links = self.browser.find_elements_by_tag_name('a')
        self.assertNotEqual(
            links,
            [],
            "No links found on this page: %s" % self.browser.current_url)
        tofind_url = self.adminurl + 'site_maps/'
        self.assertTrue(
            any(link.get_attribute('href') == tofind_url for link in links),
            "No link found to get Station Map here: %s. Searching for: %s" %
            (self.browser.current_url, tofind_url)
        )

        # Station Map link is here. So she finally click on it to see result
        self.browser.get(tofind_url)
        self.assertIn(
            'RESIF',
            self.browser.title,
            "Title should contains RESIF on %s. Current: %s." %
            (self.browser.current_url, self.browser.title))

    def test_station_to_csv_file(self):
        """
        Download the CSV Station file and check it.
        """
        # Henri needs the CSV file of all stations in order to check them on
        # LibreOffice.
        # He so get Gissmo website and log in.
        self.gissmo_login()

        # Then he goes to Station Site page and check that 'Site de test to
        # CSV' is here.
        url = self.appurl + 'stationsite/'
        self.browser.get(url)
        links = self.browser.find_elements_by_tag_name('a')
        self.assertNotEqual(
            links,
            [],
            "No links found on this page: %s" % self.browser.current_url)
        tofind_url = self.adminurl + 'test_site/'
        self.assertTrue(
            any(link.get_attribute('href') == tofind_url for link in links),
            "No link found to get Station Map here: %s. Searching for: %s" %
            (self.browser.current_url, tofind_url)
        )

        # So he clicks on it.
        for link in links:
            if link.get_attribute('href') == tofind_url:
                link.click()

        # He checks that he receives a CSV file in order to use it lately
        local_csv_filepath = '/'.join([DOWNLOAD_PATH, DOWNLOADED_FILE])
        self.assertTrue(
            os.path.exists(local_csv_filepath),
            "%s not found (when downloading %s)." %
            (local_csv_filepath, tofind_url))

        # We check the CSV file by reading it.
        self.check_csv_file(local_csv_filepath)

if __name__ == "__main__":
    unittest.main()
