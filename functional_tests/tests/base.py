# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import \
#        DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import os
import csv
import sys
import time

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
# from django.contrib.contenttypes.models import ContentType

DEFAULT_ADMIN_LOGIN = os.getenv('USER', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('PWD', 'admin')
DOWNLOAD_PATH = os.getcwd()


class FunctionalTest(LiveServerTestCase):
    """
    A set of tests that only load some webpages from Gissmo.
    """

    @classmethod
    def setUpClass(cls):
        cls.DEFAULT_ADMIN_LOGIN = DEFAULT_ADMIN_LOGIN
        cls.DEFAULT_ADMIN_PASSWORD = DEFAULT_ADMIN_PASSWORD
        cls.DOWNLOAD_PATH = DOWNLOAD_PATH
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
        super(FunctionalTest, self).setUp()
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

        self.logged = False

    def tearDown(self):
        """
        Cleaning
        """
        # close firefox
        self.browser.quit()

        # Bug: https://code.djangoproject.com/ticket/10827
        # Note: Seems to be OK since Django 1.8
        # ContentType.objects.clear_cache()

        super(FunctionalTest, self).tearDown()

    def gissmo_login(self):
        """
        Log in to Gissmo application.
        """
        if not self.logged:
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
                'Login problem on %s: no administration interface found.' %
                self.browser.current_url)
            self.logged = True

    def check_csv_file(self, filepath):
        """
        Browse the given CSV file to check if any error occured.
        """
        with open(filepath) as f:
            reader = csv.reader(f)
            try:
                # just browse rows
                for row in reader:
                    pass
            except csv.Error as e:
                sys.exit(
                    'file %s, line %d: %s' %
                    (filepath, reader.line_num, e))

    def fill_in_field(self, field):
        if field._type == 'checkbox':
            input_fields = self.browser.find_elements_by_xpath(
                "//input[@name='%s']" % field.name)
            for input_field in input_fields:
                input_value = input_field.get_attribute('value')
                is_selected = not input_field.is_selected()
                same_content = input_value in \
                    [str(value) for value in field.content]
                if same_content and is_selected:
                    input_field.click()
        elif field._type == 'autocomplete':
            # autocomplete add a kind of new input field with -autocomplete
            # at the end of the field name.
            # So we first search this input. Then we send him some value
            fieldname = field.name + '-autocomplete'
            input_field = self.browser.find_element_by_name(fieldname)
            input_field.clear()
            input_field.send_keys(field.content)
            # After a while, we select the first value displayed
            self.browser.implicitly_wait(2)
            select_element = '.yourlabs-autocomplete[data-input-id="id_' + \
                fieldname + '"] [data-value]'
            choices = self.browser.find_elements_by_css_selector(
                select_element)
            choices[0].click()
        elif field._type == Select:
            input_field = self.browser.find_element_by_name(field.name)
            input_field = Select(input_field)
            input_field.select_by_visible_text(field.content)
        else:
            input_field = self.browser.find_element_by_name(field.name)
            # Delete content first
            input_field.clear()
            input_field.send_keys(field.content)

    def check_presence_in_list(self, url, fields):
        # Stop few seconds if any problem to see what's needed
        same_url = self.browser.current_url == self.appurl + url
        if not same_url:
            time.sleep(8)

        # After saving, forms should redirect to given's url
        self.assertEqual(
            self.browser.current_url,
            self.appurl + url,
            "Problem while validating the form.")

        # Check fields
        table = self.browser.find_element_by_id('result_list')
        rows = table.find_elements_by_xpath('//tbody/tr//th')

        for field in fields:
            self.assertIn(field.content, [row.text for row in rows])

    def fill_in_form(self, url, fields, click_paths=[]):
        """
        Complete a specific form (given by URL) and validate it.
        """
        # Useless to do something without data
        if not fields:
            self.fail('No data given!')
            return
        # Login and get URL
        self.gissmo_login()
        self.browser.get(url)
        self.browser.implicitly_wait(3)

        # Prepare forms if needed
        for click_path in click_paths:
            link = self.browser.find_element_by_xpath(click_path)
            link.click()

        # Complete all fields
        for field in fields:
            self.fill_in_field(field)

        # Wait a moment to permit a developer to see if any problem
        time.sleep(3)

        # Save form
        input_save = self.browser.find_element_by_name('_save')
        input_save.send_keys(Keys.ENTER)
        self.browser.implicitly_wait(3)

    def add_item_in_admin(
            self,
            objectlisturl='/',
            fields=[],
            check=False):
        """
        The goal is to go to admin form from the given object, insert some
        given 'fields'.
        If check is True, we check one or more field as expected value in the
        'objectlisturl'.
        'fields' is a list of fields (InputField class)
        """
        url = self.appurl + objectlisturl + 'add'

        # Keep fields that needs to be checked after
        to_check_fields = []
        for field in fields:
            # aggregate fields to check
            if field.check:
                to_check_fields.append(field)

        self.fill_in_form(url, fields)

        if check:
            if not to_check_fields:
                self.fail('You have to define some field to check.')
            # check presence in list
            self.check_presence_in_list(objectlisturl, to_check_fields)
