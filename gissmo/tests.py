from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import User

DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


class HomePageTest(TestCase):

    def test_root_url_returns_404(self):
        response = self.client.get('/')
        self.assertEqual(
            response.status_code,
            404,
            "Root page shouldn't be found.")


class AdminPageTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Create super user
        """
        cls.superuser = User.objects.create_superuser(
            DEFAULT_ADMIN_LOGIN,
            'admin@mysite.com',
            DEFAULT_ADMIN_PASSWORD)

    def test_admin_page_return_200_status_code(self):
        self.client.login(
            username=DEFAULT_ADMIN_LOGIN,
            password=DEFAULT_ADMIN_PASSWORD)
        response = self.client.get('/gissmo/')
        self.assertEqual(response.status_code, 200)

    def test_login_connection(self):
        self.assertTrue(
            self.client.post(
                '/gissmo/',
                {
                    'username': DEFAULT_ADMIN_LOGIN,
                    'password': DEFAULT_ADMIN_PASSWORD,
                }),
            "Cannot login")

    def test_gissmo_shortcuts_dont_return_404_pages(self):
        links = [
            '/gissmo/gissmo/stationsite/',
            '/gissmo/gissmo/equipmodel/',
            '/gissmo/gissmo/equipment/',
            '/gissmo/gissmo/intervention/',
            '/gissmo/gissmo/actor/',
            '/gissmo/gissmo/network/',
            '/gissmo/gissmo/project/',
            '/gissmo/gissmo/equipmodeldoctype/',
            '/gissmo/gissmo/equipdoctype/',
            '/gissmo/gissmo/projectuser/',
            '/gissmo/gissmo/stationdoctype/',
            '/gissmo/gissmo/builttype/',
            '/gissmo/gissmo/equiptype/',
            '/gissmo/gissmo/calibrationunit/',
            '/gissmo/gissmo/datatype/',
            '/gissmo/gissmo/parameterequip/',
            '/gissmo/gissmo/parametervalue/',
            '/gissmo/gissmo/channel/',
            '/gissmo/gissmo/channelcode/',
            '/gissmo/xhr_station',
            '/gissmo/xhr_station_state',
            '/gissmo/xhr_equipment',
            '/gissmo/xhr_equip_state',
            '/gissmo/xhr_equip_oper',
            '/gissmo/xhr_station_position',
            '/gissmo/xhr_built',
            '/gissmo/xhr_parameter_value',
            '/gissmo/site_maps',
            '/gissmo/itineraire_maps',
            # TODO: add DATA so that dataless/ works
            # '/gissmo/dataless/',
            # TODO: LINK TO TEST, get_file/ missing
            # '/gissmo/station_xml/',
            # TODO: ValueError: invalid literal for int() with base 10: ''
            # '/gissmo/network_xml/',
            # TODO: ValueError: invalid literal for int() with base 10: ''
            # '/gissmo/station_dataless/',
            # TODO: LINK TO TEST, [A-Z0-9]{2,4} to get site_shortcut
            '/gissmo/test_site/',
            # '/gissmo/chaining/',
        ]
        # login first to the application
        self.client.login(
            username=DEFAULT_ADMIN_LOGIN,
            password=DEFAULT_ADMIN_PASSWORD)
        # check then urls
        for link in links:
            response = self.client.get(link)
            self.assertNotEqual(
                response.status_code,
                404,
                "404 status code for: %s" % link)
