from __future__ import unicode_literals
from django.test import TestCase

DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


class HomePageTest(TestCase):

    def test_root_url_returns_302(self):
        response = self.client.get('/')
        self.assertEqual(
            response.status_code,
            302,
            "Root page should be redirected!")
