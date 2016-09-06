# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import FunctionalTest
from .input_field import InputField

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from datetime import datetime
from time import sleep

from django.utils.timezone import make_aware

from gissmo.models import (
    ChainConfig,
    Channel,
    ChannelCode,
    ConfigEquip,
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


class ChannelTest(FunctionalTest):

    def setUp(self):
        super(ChannelTest, self).setUp()
        # Linked project
        self.project = Project.objects.create(
            name='ADEME',
            manager=self.superuser)
        self.superuser.groups.add(self.project)
        # Organism
        self.eost = Organism.objects.create(
            name='EOST',
            _type=Organism.OBSERVATORY)
        # Station
        station_date = datetime.strptime('2016-06-04', '%Y-%m-%d')
        self.station = StationSite.objects.create(
            site_type=StationSite.SITE_TEST,
            station_code='CHMF',
            operator=self.eost,
            project=self.project,
            actor=self.superuser,
            creation_date=make_aware(station_date))
        # Equipment's Model
        self.supertype = EquipSupertype.objects.create(
            equip_supertype_name='01. Scientifique',  # WARNING: hard-coded
            presentation_rank='1')
        self._type = EquipType.objects.create(
            equip_supertype=self.supertype,
            presentation_rank='1',
            equip_type_name='Datalogger')
        self.model = EquipModel.objects.create(
            equip_type=self._type,
            equip_model_name='Centaur')
        # Parameter 'Number of channels' (3 or 6)
        self.parameter1 = ParameterEquip.objects.create(
            equip_model=self.model,
            parameter_name='Number of channels')
        self.param1value1 = ParameterValue.objects.create(
            parameter=self.parameter1,
            value='3',
            default_value=True)
        self.param1value2 = ParameterValue.objects.create(
            parameter=self.parameter1,
            value='6',
            default_value=False)
        # Parameter 'Gain' (+2 or +5)
        self.parameter2 = ParameterEquip.objects.create(
            equip_model=self.model,
            parameter_name='Gain')
        self.param2value1 = ParameterValue.objects.create(
            parameter=self.parameter2,
            value='+2',
            default_value=True)
        self.param2value2 = ParameterValue.objects.create(
            parameter=self.parameter2,
            value='+5',
            default_value=False)
        # Equipment
        purchase_date = datetime.strptime('2016-01-01', '%Y-%m-%d')
        self.equip = Equipment.objects.create(
            equip_model=self.model,
            serial_number='123456',
            owner=self.eost,
            stockage_site=self.station,
            purchase_date=make_aware(purchase_date),
            actor=self.superuser)
        # Add previous equipment on station after having test it
        running_date = datetime.strptime('2016-01-02', '%Y-%m-%d')
        self.intervention = Intervention.objects.create(
            station=self.station,
            intervention_date=make_aware(running_date))
        self.intervequip = IntervEquip.objects.create(
            intervention=self.intervention,
            equip_action=2,  # Test
            equip=self.equip,
            equip_state=3,  # Running
            station=self.station)
        # Network
        self.network = Network.objects.create(
            network_code='XX')

    def test_channelcode_creation(self):
        """
        Create a simple channel code.
        """
        code = InputField(
            name='channel_code',
            content='HHZ',
            check=True)

        fields = [code]

        self.add_item_in_admin('channelcode/', fields, check=True)

    def test_channel_creation(self):
        """
        Create a channel. Then check Channel configuration: Should match
        equipment one.
        To check that this is not Equipment's model configuration,
        we change equipment parameter 1 to the default value that is not the
        default one!
        """
        # initial needed data
        ChannelCode.objects.create(channel_code='HHZ')
        equip_param1 = ConfigEquip.objects.filter(
            equipment=self.equip,
            parameter=self.parameter1).first()
        self.assertNotEqual(equip_param1, None, 'Missing parameter!')
        equip_param1.value = self.param1value2
        equip_param1.save()

        # We login to the application in order to add a Channel on CHMF
        self.gissmo_login()
        url = self.appurl + 'channel/add'
        self.browser.get(url)

        # So we complete some fields
        network = InputField(
            name='network',
            content='XX',
            _type=Select)
        station = InputField(
            name='station',
            content='CHMF',
            _type=Select)
        code = InputField(
            name='channel_code',
            content='HHZ',
            _type=Select)
        longitude = InputField(name='longitude', content='48.5793')
        latitude = InputField(name='latitude', content='7.763')
        elevation = InputField(name='elevation', content='200.0')
        rate = InputField(
            name='sample_rate',
            content='100')
        date = InputField(
            name='start_date_0',
            content='2016-06-14')
        fields = [
            network,
            station,
            code,
            longitude,
            latitude,
            elevation,
            rate,
            date]
        for field in fields:
            self.fill_in_field(field)

        # Then we add an acquisition chain composed of Datalogger
        link = self.browser.find_element_by_xpath(
            '//a[. = "Add another Acquisition chain"]')
        link.click()
        self.browser.implicitly_wait(3)

        _type = InputField(
            name='chain_set-0-order',
            content='DataLogger',
            _type=Select)
        equip = InputField(
            name='chain_set-0-equip',
            content=str(self.equip),
            _type=Select)
        # As it takes time to display equipment, we make a pause after _type
        self.fill_in_field(_type)
        sleep(1)
        self.fill_in_field(equip)

        # Save form
        sleep(3)
        input_save = self.browser.find_element_by_name('_save')
        input_save.send_keys(Keys.ENTER)
        self.browser.implicitly_wait(3)

        # Check chain configuration. Should match equipment one.
        chain = ChainConfig.objects.filter(
            chain__equip=self.equip,
            parameter=self.parameter1).first()
        self.assertNotEqual(chain, None, 'No chain found!')
        current = chain.value
        expected = self.param1value2
        self.assertEqual(
            current,
            expected,
            'Wrong value: %s. Should be %s.' % (current, expected))

    def test_check_station_button(self):
        """
        After channel creation, as we linked channel to a given station,
        we check that "Check station" button exists and redirect to the station
        """
        # Create channel
        self.channel_code = ChannelCode.objects.create(channel_code='HHZ')
        creation_date = datetime.strptime('2016-09-07', '%Y-%m-%d')
        self.channel_1 = Channel.objects.create(
            network=self.network,
            station=self.station,
            channel_code=self.channel_code,
            longitude='48.5793',
            latitude='7.763',
            elevation='200.0',
            depth='0',
            azimuth='90',
            dip='-90',
            sample_rate='100',
            start_date=make_aware(creation_date))

        # Login to Gissmo and go to the channel
        self.gissmo_login()
        url = '%schannel/%s' % (self.appurl, self.channel_1.id)
        self.browser.get(url)

        # Search link then click on it
        link = self.browser.find_element_by_xpath('//a[. = "Check station"]')
        link.click()

        # Check redirection URL. Should be those from station
        current = self.browser.current_url
        expected = '%sstationsite/%s/' % (self.appurl, self.station.id)
        self.assertEqual(
            current,
            expected,
            'Wrong URL: %s. Should be: %s' % (current, expected))
