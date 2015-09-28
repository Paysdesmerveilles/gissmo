from django.test import TestCase
from django.contrib.auth.models import User

DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'

class HomePageTest(TestCase):

    def test_root_url_returns_404(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404, 
            "Root page shouldn't be found.")

class AdminPageTest(TestCase):

    def setUp(self):
        """
        Create super user
        """
        self.superuser = User.objects.create_superuser(DEFAULT_ADMIN_LOGIN, 
            'admin@mysite.com', DEFAULT_ADMIN_PASSWORD)

    def test_admin_page_return_200_status_code(self):
        response = self.client.get('/gissmo/')
        self.assertEqual(response.status_code, 200)

    def test_login_connection(self):
        self.assertTrue(self.client.login(username=DEFAULT_ADMIN_LOGIN,
            password=DEFAULT_ADMIN_PASSWORD), "Cannot login")

    def test_gissmo_shortcuts_dont_return_404_pages(self):
        links = [
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
            'channelcode/',
            'xhr_station/',
            'xhr_station_state/',
            'xhr_equipment/',
            'xhr_equip_state/',
            'xhr_equip_oper/',
            'xhr_station_position/',
            'xhr_built/',
            'xhr_parameter_value/',
            'site_maps/',
            'itineraire_maps/',
            # TODO: add DATA so that dataless/ works
            #'dataless/',
            # TODO: LINK TO TEST, get_file/ missing
            'station_xml/',
            # TODO: ValueError: invalid literal for int() with base 10: ''
            #'network_xml/',
            # TODO: ValueError: invalid literal for int() with base 10: ''
            #'station_dataless/',
            # TODO: LINK TO TEST, [A-Z0-9]{2,4} to get site_shortcut
            'test_site/',
            'chaining/',
        ]
        # login first to the application
        self.client.post('/gissmo/',
            {
                'username': DEFAULT_ADMIN_LOGIN, 
                'password': DEFAULT_ADMIN_PASSWORD,
            })
        # check then urls
        for link in links:
            url = '/gissmo/' + link
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, "Wrong response status \
code for %s: return %s" % (url, response.status_code))
