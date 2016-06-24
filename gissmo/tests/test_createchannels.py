from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.test import TestCase
from django.utils.timezone import make_aware

from gissmo.admin import StationSiteAdmin
from gissmo.forms import CreateChannelForm
from gissmo.models import (
    Chain,
    ChainConfig,
    Channel,
    ChannelCode,
    EquipModel,
    EquipSupertype,
    EquipType,
    Equipment,
    IntervEquip,
    Intervention,
    Network,
    Organism,
    ParameterEquip,
    ParameterValue,
    Project,
    StationSite,
)
from gissmo.views import createchannels_process

from datetime import datetime

DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


class CreateChannelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Station
        cls.superuser = User.objects.create_superuser(
            DEFAULT_ADMIN_LOGIN,
            'admin@mysite.com',
            DEFAULT_ADMIN_PASSWORD)
        cls.project = Project.objects.create(
            name='ALL',
            manager=cls.superuser)
        cls.eost = Organism.objects.create(
            name='EOST',
            _type=Organism.OBSERVATORY)
        cls.station = StationSite.objects.create(
            site_type=StationSite.SITE_TEST,
            station_code='CHMF',
            latitude='47.2483',
            longitude='6.6517',
            elevation='809',
            operator=cls.eost,
            project=cls.project,
            actor=cls.superuser,
            creation_date='2015-10-04')
        # For channels
        cls.HHN_code = ChannelCode.objects.create(
            channel_code='HHN')
        cls.HHZ_code = ChannelCode.objects.create(
            channel_code='HHZ')
        cls.HHE_code = ChannelCode.objects.create(
            channel_code='HHE')
        cls.network = Network.objects.create(
            network_code='FR')
        # Equipment's Model
        cls.supertype = EquipSupertype.objects.create(
            equip_supertype_name='01. Scientifique',  # WARNING: hard-coded
            presentation_rank='1')
        cls._type = EquipType.objects.create(
            equip_supertype=cls.supertype,
            presentation_rank='1',
            equip_type_name='Datalogger')
        cls.model = EquipModel.objects.create(
            equip_type=cls._type,
            equip_model_name='Centaur')
        cls.parameter1 = ParameterEquip.objects.create(
            equip_model=cls.model,
            parameter_name='Number of channels')
        cls.param1value1 = ParameterValue.objects.create(
            parameter=cls.parameter1,
            value='3',
            default_value=True)
        cls.param1value2 = ParameterValue.objects.create(
            parameter=cls.parameter1,
            value='6',
            default_value=False)
        # Equipment
        purchase_date = datetime.strptime('2016-01-01', '%Y-%m-%d')
        cls.equip = Equipment.objects.create(
            equip_model=cls.model,
            serial_number='123456',
            owner=cls.eost,
            stockage_site=cls.station,
            purchase_date=make_aware(purchase_date),
            actor=cls.superuser)
        # Add previous equipment on station after having test it
        running_date = datetime.strptime('2016-01-02', '%Y-%m-%d')
        cls.intervention = Intervention.objects.create(
            station=cls.station,
            intervention_date=make_aware(running_date))
        cls.intervequip = IntervEquip.objects.create(
            intervention=cls.intervention,
            equip_action=2,  # Test
            equip=cls.equip,
            equip_state=3,  # Running
            station=cls.station)

        # Miscellaneous
        cls.url = \
            '/gissmo/stationsite/%s/createchannels/' % cls.station.id

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

    def get_createchannels_forms(self, request):
        a = StationSiteAdmin(StationSite, admin.site)
        ChainFormSet = a.createchannels_formset(self.station)
        return CreateChannelForm(request.POST), ChainFormSet(request.POST)

    def test_createchannels_page_loading(self):
        """
        Check that Create channel wizard is available.
        """
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            200,
            "Page loading status: %s" % response.status_code)
        templates = []
        template = 'createchannels_view.html'
        for t in response.templates:
            templates.append(t.name)
        self.assertIn(template, templates, "%s missing template." % template)

    def test_create_3_channels(self):
        """
        Create 3 channels:
          - HHN
          - HHZ
          - HHE
        with "Add 3 channels" button wizard
        """
        channel_date = datetime.strptime('2016-05-28', '%Y-%m-%d')
        channel_time = '11:00:00'

        request = self.django_post_request()

        request.POST['code'] = 'HH'
        request.POST['network'] = self.network.id
        request.POST['location'] = '00'
        request.POST['rate'] = 101
        request.POST['date_0'] = make_aware(channel_date)
        request.POST['date_1'] = channel_time

        # Fill in forms
        form, chain_formset = self.get_createchannels_forms(request)

        # Check form validation
        self.assertEqual(
            form.is_valid(),
            True,
            "Invalid form: %s" % form.errors)

        # Process form
        createchannels_process(
            request,
            form,
            chain_formset,
            self.station.id, {})

        # Check channels:
        #  - we should have 3 channels for this station
        #  - HHZ, HHN and HHE
        channels = Channel.objects.filter(station=self.station)
        channel_count = channels.count()
        self.assertEqual(
            channel_count,
            3,
            "Should have 3 channels. Current: %s" % channel_count)
        for code in ['HHZ', 'HHN', 'HHE']:
            channel = Channel.objects.filter(
                station=self.station,
                channel_code__channel_code=code)
            self.assertNotEqual(
                channel,
                [],
                "%s Channel not found." % code)

    def test_create_channel_with_equipment(self):
        """
        Create 3 channels with an equipment to check default parameters
        """
        channel_date = datetime.strptime('2016-05-28', '%Y-%m-%d')
        channel_time = '11:00:00'

        request = self.django_post_request()

        request.POST['code'] = 'HH'
        request.POST['network'] = self.network.id
        request.POST['location'] = '00'
        request.POST['rate'] = 101
        request.POST['date_0'] = make_aware(channel_date)
        request.POST['date_1'] = channel_time
        request.POST['form-0-order'] = 3  # Datalogger
        request.POST['form-0-equipment'] = self.equip.id

        # Fill in forms
        form, chain_formset = self.get_createchannels_forms(request)

        # Check form validation
        self.assertEqual(
            form.is_valid(),
            True,
            "Invalid form: %s" % form.errors)

        # Process form
        createchannels_process(
            request,
            form,
            chain_formset,
            self.station.id, {})

        # Check channels:
        #  - we should have 3 channels for this station
        #  - each channel should have an equipment and a configuration line
        channels = Channel.objects.filter(station=self.station)
        channel_count = channels.count()
        self.assertEqual(
            channel_count,
            3,
            "Should have 3 channels. Current: %s" % channel_count)
        for channel in channels:
            code = channel.channel_code.channel_code
            chains = Chain.objects.filter(channel=channel)
            self.assertNotEqual(
                chains,
                [],
                "No chain found for %s." % code)
            for chain in chains:
                self.assertEqual(
                    chain.equip,
                    self.equip,
                    "Wrong equipment linked. Current: %s" % self.equip)
                configs = ChainConfig.objects.filter(chain=chain)
                self.assertNotEqual(
                    configs,
                    [],
                    "No configuration found for channel %s" % code)
