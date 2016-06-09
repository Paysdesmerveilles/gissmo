from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import User


DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


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
                '/',
                {
                    'username': DEFAULT_ADMIN_LOGIN,
                    'password': DEFAULT_ADMIN_PASSWORD,
                }),
            "Cannot login")

    def test_gissmo_shortcuts_dont_return_404_pages(self):
        links = [
            '/gissmo/organism/',
            '/gissmo/builttype/',
            '/gissmo/calibrationunit/',
            '/gissmo/channel/',
            '/gissmo/channelcode/',
            '/gissmo/datatype/',
            '/gissmo/equipdoctype/',
            '/gissmo/equipment/',
            '/gissmo/equipmodel/',
            '/gissmo/equipmodeldoctype/',
            '/gissmo/equiptype/',
            '/gissmo/forbiddenequipmentmodel/',
            '/gissmo/groundtype/',
            '/gissmo/intervention/',
            '/gissmo/network/',
            '/gissmo/parameterequip/',
            '/gissmo/parametervalue/',
            '/gissmo/project/',
            '/gissmo/stationdoctype/',
            '/gissmo/stationsite/',
            '/xhr_station',
            '/xhr_station_state',
            '/xhr_equipment',
            '/xhr_equip_state',
            '/xhr_equip_oper',
            '/xhr_station_position',
            '/xhr_built',
            '/xhr_parameter_value',
            '/site_maps',
            '/itineraire_maps',
            # TODO: LINK TO TEST, get_file/ missing
            # '/station_xml/',
            # TODO: LINK TO TEST, [A-Z0-9]{2,4} to get site_shortcut
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
