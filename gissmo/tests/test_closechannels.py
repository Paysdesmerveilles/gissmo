from __future__ import unicode_literals
from django.test import TestCase
from django.contrib import admin
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.utils.timezone import make_aware

from gissmo.models import (
    Affiliation,
    Channel,
    ChannelCode,
    Network,
    Project,
    StationSite,
)
from gissmo.admin import StationSiteAdmin
from gissmo.views import closechannels_process

from datetime import datetime

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
            name='ALL',
            manager=cls.superuser)
        cls.eost = Affiliation.objects.create(
            name='EOST',
            _type=Affiliation.OBSERVATORY)
        cls.station = StationSite.objects.create(
            site_type=StationSite.SITE_TEST,
            station_code='CHMF',
            operator=cls.eost,
            project=cls.project,
            actor=cls.superuser,
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
        channels_date = datetime.strptime('2016-02-04', '%Y-%m-%d')
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
            start_date=make_aware(channels_date))
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
            start_date=make_aware(channels_date))
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
            start_date=make_aware(channels_date))
        cls.url = \
            '/gissmo/gissmo/stationsite/%s/closechannels/' % cls.station.id

    def login(self):
        self.client.login(
            username=DEFAULT_ADMIN_LOGIN,
            password=DEFAULT_ADMIN_PASSWORD)

    def django_post_request(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['form-TOTAL_FORMS'] = 1
        request.POST['form-INITIAL_FORMS'] = 0
        request.POST['form-MAX_NUM_FORMS'] = ''
        user = authenticate(
            username=DEFAULT_ADMIN_LOGIN,
            password=DEFAULT_ADMIN_PASSWORD)
        request.user = user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def get_closechannels_formset(self, request):
        a = StationSiteAdmin(StationSite, admin.site)
        FormSet = a.closechannels_formset(self.station)
        formset = FormSet(request.POST)
        return formset

    def test_closechannels_page_loading(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            200,
            "Page loading status: %s" % response.status_code)
        templates = []
        template = 'closechannels_view.html'
        for t in response.templates:
            templates.append(t.name)
        self.assertIn(template, templates, "%s missing template." % template)

    def test_single_closing_channel(self):
        channel_datekey = 'form-0-%s_0' % self.channel_N.id
        channel_timekey = 'form-0-%s_1' % self.channel_N.id
        channel_date = datetime.strptime('2016-02-27', '%Y-%m-%d')
        channel_time = '15:00:00'

        request = self.django_post_request()
        request.POST[channel_datekey] = make_aware(channel_date)
        request.POST[channel_timekey] = channel_time

        formset = self.get_closechannels_formset(request)

        self.assertEqual(
            formset.is_valid(),
            True,
            "Invalid form: %s" % formset.errors)

        for f in formset.cleaned_data:
            closechannels_process(request, f, self.station.id, {})

        tested_channel_N = Channel.objects.get(pk=self.channel_N.id)
        tested_date = make_aware(
            datetime.strptime("2016-02-27 15:00:00", '%Y-%m-%d %H:%M:%S'))
        tested_channel_Z = Channel.objects.get(pk=self.channel_Z.id)
        tested_channel_E = Channel.objects.get(pk=self.channel_E.id)
        self.assertEqual(
            tested_channel_N.end_date,
            tested_date,
            "Channel N: end_date should be set.")
        date = tested_channel_Z.end_date
        self.assertEqual(
            date,
            None,
            "Channel Z: no date expected! Current: %s" % date)
        date = tested_channel_E.end_date
        self.assertEqual(
            date,
            None,
            "Channel E: no date expected! Current: %s" % date)

    def test_closing_all_channels(self):
        date = datetime.strptime('2016-02-27', '%Y-%m-%d')
        time = '15:00:00'
        tested_date = make_aware(
            datetime.strptime("2016-02-27 15:00:00", '%Y-%m-%d %H:%M:%S'))
        request = self.django_post_request()
        request.POST['form-0-date_0'] = make_aware(date)
        request.POST['form-0-date_1'] = time
        request.POST['form-0-all_channels'] = True

        formset = self.get_closechannels_formset(request)

        self.assertEqual(
            formset.is_valid(),
            True,
            "Invalid form: %s" % formset.errors)

        for f in formset.cleaned_data:
            closechannels_process(request, f, self.station.id, {})

        channel_codes = ['N', 'Z', 'E']
        for code in channel_codes:
            tested_channel = getattr(self, 'channel_%s' % code, None)
            channel = Channel.objects.get(pk=tested_channel.id)
            self.assertEqual(
                channel.end_date,
                tested_date,
                "Channel %s: end_date should be set.")
