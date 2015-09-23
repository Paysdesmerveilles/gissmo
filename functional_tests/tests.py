# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import unittest
import os
import csv

from docker import Client

DOCKER_CONTAINER_NAME = 'gissmo'
DOCKER_CONTAINER_DEFAULT_PORT = '8000'
DEFAULT_ADMIN_LOGIN = 'olivier'
DEFAULT_ADMIN_PASSWORD = 'olivier'
DOWNLOAD_PATH = os.getcwd()
DOWNLOADED_FILE = 'test_site.csv'

class SimpleTest(unittest.TestCase):
    """
    A set of tests that only load some webpages from Gissmo.
    """

    def setUp(self):
        """
        Launch Firefox as Web Testing Platform.
        """
        # Set Firefox profile to DL CSV files
        fp = webdriver.FirefoxProfile()

        fp.set_preference("browser.download.folderList",2)
        fp.set_preference("browser.download.manager.showWhenStarting",False)
        fp.set_preference("browser.download.dir", DOWNLOAD_PATH)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

        self.browser = webdriver.Firefox(firefox_profile=fp)
        self.browser.implicitly_wait(3)
        # search for gissmo instance IP (in Docker)
        c = Client(base_url='unix://var/run/docker.sock')
        container_metadata = c.inspect_container(DOCKER_CONTAINER_NAME)
        try:
            self.ip = container_metadata['NetworkSettings']['IPAddress']
        except KeyError as e:
            self.ip = 'localhost'
        try:
            self.ports = container_metadata['NetworkSettings']['Ports']
        except KeyError as e:
            self.ports = None
        self.port = DOCKER_CONTAINER_DEFAULT_PORT
        # DOCKER BUG: Don't know why 8000 is the default one
#        if self.ports:
#            try:
#                self.port = self.ports['8000/tcp'][0]['HostPort']
#            except KeyError as e:
#                self.port = None
        self.url = 'http://%s:%s/' % (self.ip, self.port)
        self.adminurl = self.url + 'gissmo/'
        self.appurl = self.adminurl + 'gissmo/'

    def tearDown(self):
        """
        Close Browser.
        Clean working directory:
          - test_site.csv file
        """
        self.browser.quit()
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
        inputlogin = self.browser.find_element_by_id('id_username')
        inputpassword = self.browser.find_element_by_id('id_password')
        inputlogin.send_keys(DEFAULT_ADMIN_LOGIN)
        inputpassword.send_keys(DEFAULT_ADMIN_PASSWORD)
        inputpassword.send_keys(Keys.ENTER)
        # Stop tests if login failed
        self.assertIn('Site administration', self.browser.title, 
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
                sys.exit('file %s, line %d: %s' % 
                    (filepath, reader.line_num, e))

    def test_can_get_main_pages(self):
        """
        Check that each page don't send a 404 error message
        """
        # Martin Dupont start using the site. He goes to check the website 
        #+ homepage.
        url = self.url
        self.browser.get(url)

        # He receive a 404 error: Page not found. He remembers that we should 
        #+ type /gissmo after the URL
        self.assertIn('Page not found', self.browser.title, 
            'Problem loading %s' % self.browser.current_url)
        url = self.adminurl
        self.browser.get(url)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Gissmo', header_text, 
            'Problem loading %s' % self.browser.current_url)

        # He puts his username and password to connect the admin interface
        self.assertIn('Log in', self.browser.title, 
            'Problem loading %s: Not login page' % self.browser.current_url)
        inputlogin = self.browser.find_element_by_id('id_username')
        inputpassword = self.browser.find_element_by_id('id_password')
        inputlogin.send_keys(DEFAULT_ADMIN_LOGIN)
        inputpassword.send_keys(DEFAULT_ADMIN_PASSWORD)

        # When he hits enter, the page updates, and now administration appears
        inputpassword.send_keys(Keys.ENTER)
        self.assertIn('Site administration', self.browser.title, 
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
            self.assertNotIn('Page not found', self.browser.title, 
                "Not found URL: %s" % self.browser.current_url)
            self.assertIn('Select', self.browser.title,
                "No 'select' on title. %s" % self.browser.current_url)
            self.assertIn('to change', self.browser.title,
                "No 'to change' on title. %s" % self.browser.current_url)
        
        # As Martin is curious, he changes the URL using imagination.
        # But the application said "Page not found".
        url = self.appurl + 'sdflkj'
        self.browser.get(url)
        self.assertIn('Page not found', self.browser.title,
            "This page SHOULD NOT be found! %s" % self.browser.current_url)

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
        self.assertNotEqual(links, [], 
            "No links found on this page: %s" % self.browser.current_url)
        tofind_url = self.adminurl + 'site_maps/'
        self.assertTrue(
            any(link.get_attribute('href') == tofind_url for link in links),
            "No link found to get Station Map here: %s. Searching for: %s" % 
                (self.browser.current_url, tofind_url)
        )

        # Station Map link is here. So she finally click on it to see result
        self.browser.get(tofind_url)
        self.assertIn('RESIF', self.browser.title,
            "Title should contains RESIF on %s. Current: %s." % 
            (self.browser.current_url, self.browser.title))

    def test_station_to_csv_file(self):
        """
        Download the CSV Station file and check it.
        """
        # Henri needs the CSV file of all stations in order to check them on
        #+ LibreOffice.
        # He so get Gissmo website and log in.
        self.gissmo_login()
        
        # Then he goes to Station Site page and check that 'Site de test to CSV'
        #+ is here.
        url = self.appurl + 'stationsite/'
        self.browser.get(url)
        links = self.browser.find_elements_by_tag_name('a')
        self.assertNotEqual(links, [], 
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
        self.assertTrue(os.path.exists(local_csv_filepath), 
            "%s not found (when downloading %s)." % 
                (local_csv_filepath, tofind_url))
        
        # We check the CSV file by reading it.
        self.check_csv_file(local_csv_filepath)

if __name__ == "__main__":
    unittest.main()
