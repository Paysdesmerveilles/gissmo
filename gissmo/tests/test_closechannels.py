from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import User

from gissmo.models import (
    Actor,
    Channel,
    ChannelCode,
    Network,
    Project,
    StationSite)

DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


class CloseChannelsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Needed data to launch test on channels.
        We need a user, a station and some equipments on it.
        """
        cls.superuser = User.objects.create_superuser(
            DEFAULT_ADMIN_LOGIN,
            'admin@mysite.com',
            DEFAULT_ADMIN_PASSWORD)
        cls.project = Project.objects.create(
            project_name='ALL',
            manager=cls.superuser)
        cls.eost_actor = Actor.objects.create(
            actor_name='EOST',
            actor_type=Actor.OBSERVATOIRE)
        # Station creation need to know which actor create it.
        # We so create an actor for the given superuser.
        cls.superuser_actor = Actor.objects.create(
            actor_name=DEFAULT_ADMIN_LOGIN,
            actor_type=Actor.AUTRE)
        cls.station = StationSite.objects.create(
            site_type=StationSite.SITE_TEST,
            station_code='CHMF',
            operator=cls.eost_actor,
            project=cls.project,
            actor=cls.superuser_actor,
            creation_date='2015-10-04')
        # Create some channel codes to create channels
        cls.HHN_code = ChannelCode.objects.create(
            channel_code='HHN')
        cls.HHZ_code = ChannelCode.objects.create(
            channel_code='HHZ')
        cls.HHE_code = ChannelCode.objects.create(
            channel_code='HHE')
        cls.network = Network.objects.create(
            network_code='FR')
        cls.channel_N = Channel.objects.create(
            station=cls.station,
            network=cls.network,
            channel_code=cls.HHN_code,
            latitude='48.5793',
            longitude='7.763',
            elevation='200.0',
            depth='0.0',
            azimuth='0.0',
            dip='0.0',
            sample_rate=20.0,
            start_date='2016-02-04')
        cls.channel_Z = Channel.objects.create(
            station=cls.station,
            network=cls.network,
            channel_code=cls.HHZ_code,
            latitude='48.5793',
            longitude='7.763',
            elevation='200.0',
            depth='0.0',
            azimuth='0.0',
            dip='0.0',
            sample_rate=0.0,
            start_date='2016-02-04')
        cls.channel_E = Channel.objects.create(
            station=cls.station,
            network=cls.network,
            channel_code=cls.HHE_code,
            latitude='48.5793',
            longitude='7.763',
            elevation='200.0',
            depth='0.0',
            azimuth='0.0',
            dip='90.0',
            sample_rate=10.0,
            start_date='2016-02-04')

    def login(self):
        self.client.login(
            username=DEFAULT_ADMIN_LOGIN,
            password=DEFAULT_ADMIN_PASSWORD)

    def test_closechannels_page_loading(self):
        self.fail("TODO")

    def test_common_date_alone_raise_an_error(self):
        self.login()
        self.fail("TODO")

    def test_checkbox_alone_raise_an_error(self):
        self.fail("TODO")

    def test_single_closing_channel(self):
        self.fail("TODO")

    def test_closing_all_channels(self):
        self.fail("TODO")
