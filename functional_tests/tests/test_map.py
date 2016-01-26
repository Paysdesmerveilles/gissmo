from __future__ import unicode_literals
from .base import FunctionalTest


class MapTest(FunctionalTest):

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
