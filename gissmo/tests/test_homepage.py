from __future__ import unicode_literals
from django.test import TestCase


class HomePageTest(TestCase):

    def test_root_url_returns_302(self):
        response = self.client.get('/')
        self.assertEqual(
            response.status_code,
            302,
            "Root page should be redirected!")
