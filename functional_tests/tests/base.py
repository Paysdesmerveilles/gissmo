# -*- coding: utf-8 -*-
from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import \
#        DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import os
import csv
import sys

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

DEFAULT_ADMIN_LOGIN = os.getenv('USER', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('PWD', 'admin')
DOWNLOAD_PATH = os.getcwd()
DOWNLOADED_FILE = 'test_site.csv'


class FunctionalTest(LiveServerTestCase):
    """
    A set of tests that only load some webpages from Gissmo.
    """

    @classmethod
    def setUpClass(cls):
        cls.DEFAULT_ADMIN_LOGIN = DEFAULT_ADMIN_LOGIN
        cls.DEFAULT_ADMIN_PASSWORD = DEFAULT_ADMIN_PASSWORD
        cls.DOWNLOAD_PATH = DOWNLOAD_PATH
        cls.DOWNLOADED_FILE = DOWNLOADED_FILE
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super(FunctionalTest, cls).setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super(FunctionalTest, cls).tearDownClass()

    def setUp(self):
        """
        Launch Firefox as Web Testing Platform.
        """
        self.superuser = User.objects.create_superuser(
            self.DEFAULT_ADMIN_LOGIN,
            'admin@mysite.com',
            self.DEFAULT_ADMIN_PASSWORD)
        # Set Firefox profile to DL CSV files
        fp = webdriver.FirefoxProfile()

        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", self.DOWNLOAD_PATH)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

#        # Create a connection to a Remote Selenium Node
#        self.browser = webdriver.Remote(
#            command_executor='http://selenium:4444/wd/hub',
#            desired_capabilities=DesiredCapabilities.FIREFOX,
#            browser_profile=fp,
#        )

        self.browser = webdriver.Firefox(firefox_profile=fp)
        self.browser.implicitly_wait(3)

        self.url = self.server_url + '/'
        self.adminurl = self.url + 'gissmo/'
        self.appurl = self.adminurl + 'gissmo/'

    def tearDown(self):
        """
        Cleaning
        """
        # close firefox
        self.browser.quit()

        # Bug: https://code.djangoproject.com/ticket/10827
        ContentType.objects.clear_cache()

        # clean working directory
        csv_filename = self.DOWNLOADED_FILE
        filepath = '/'.join([self.DOWNLOAD_PATH, csv_filename])
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
        inputlogin.send_keys(self.DEFAULT_ADMIN_LOGIN)
        inputpassword.send_keys(self.DEFAULT_ADMIN_PASSWORD)
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

    def add_item_in_admin_and_check_presence_in_list(
            self,
            objectlisturl='/',
            fields=[]):
        """
        The goal is to go to admin form from the given object, insert some
        given 'fields', and check one or more field as expected value in the
        'objectlisturl'.
        'fields' is a list of fields (InputField class)
        """
        # Useless to do something without data
        if not fields:
            self.fail('No data given!')
            return
        # Login and get URL
        self.gissmo_login()
        url = self.appurl + objectlisturl + 'add'
        self.browser.get(url)

        # Complete all fields and keep those that needs to be checked after
        to_check_fields = []
        for field in fields:
            if field._type == 'checkbox':
                input_fields = self.browser.find_elements_by_xpath(
                    "//input[@name='%s']" % field.name)
                for input_field in input_fields:
                    input_value = input_field.get_attribute('value')
                    is_selected = not input_field.is_selected()
                    same_content = input_value in [str(value) for value in field.content]
                    if same_content and is_selected:
                        input_field.click()
            elif field._type == Select:
                input_field = self.browser.find_element_by_name(field.name)
                input_field = Select(input_field)
                input_field.select_by_visible_text(field.content)
            else:
                input_field = self.browser.find_element_by_name(field.name)
                input_field.send_keys(field.content)

            # aggregate fields to check
            if field.check:
                to_check_fields.append(field)

        if not to_check_fields:
            self.fail('You have to define some field to check.')

        # Save form
        input_save = self.browser.find_element_by_name('_save')
        input_save.send_keys(Keys.ENTER)

        # After saving, forms should redirect to object's list
        self.assertEqual(
            self.browser.current_url,
            self.appurl + objectlisturl,
            "Problem while validating the form.")

        # Check fields
        table = self.browser.find_element_by_id('result_list')
        rows = table.find_elements_by_xpath('//tbody/tr//th')

        for to_check_field in to_check_fields:
            self.assertIn(to_check_field.content, [row.text for row in rows])
