from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import User
from gissmo import __version__ as gissmo_version


DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


class SiteMapTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            DEFAULT_ADMIN_LOGIN,
            'admin@mysite.com',
            DEFAULT_ADMIN_PASSWORD)

    def test_site_map_application_title(self):
        self.client.login(
            username=DEFAULT_ADMIN_LOGIN,
            password=DEFAULT_ADMIN_PASSWORD)
        response = self.client.get('/site_maps/')
        title = response.context[0].get('site_header', None)
        expect = 'Gissmo %s' % gissmo_version
        self.assertEqual(title, expect, "Wrong site header: %s" % title)
