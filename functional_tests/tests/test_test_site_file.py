from .base import FunctionalTest

import os


class TestSiteCSVFileTest(FunctionalTest):

    def test_station_to_csv_file(self):
        """
        Download the CSV Station file and check it.
        """
        # Henri needs the CSV file of all stations in order to check them on
        # LibreOffice.
        # He so get Gissmo website and log in.
        self.gissmo_login()

        # Then he goes to Station Site page and check that 'Site de test to
        # CSV' is here.
        url = self.appurl + 'stationsite/'
        self.browser.get(url)
        links = self.browser.find_elements_by_tag_name('a')
        self.assertNotEqual(
            links,
            [],
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
        local_csv_filepath = '/'.join([
            self.DOWNLOAD_PATH,
            self.DOWNLOADED_FILE])
        self.assertTrue(
            os.path.exists(local_csv_filepath),
            "%s not found (when downloading %s)." %
            (local_csv_filepath, tofind_url))

        # We check the CSV file by reading it.
        self.check_csv_file(local_csv_filepath)
