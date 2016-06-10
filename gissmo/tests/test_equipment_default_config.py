from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

from gissmo.models import (
    Channel,
    ChannelCode,
    ConfigEquip,
    EquipModel,
    EquipSupertype,
    EquipType,
    Equipment,
    Network,
    Organism,
    ParameterEquip,
    ParameterValue,
    Project,
    StationSite,
)

from datetime import datetime

DEFAULT_ADMIN_LOGIN = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


class ChainConfigTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Needed data
        """
        # Station owner
        cls.superuser = User.objects.create_superuser(
            DEFAULT_ADMIN_LOGIN,
            'admin@mysite.com',
            DEFAULT_ADMIN_PASSWORD)
        # Linked project
        cls.project = Project.objects.create(
            name='ALL',
            manager=cls.superuser)
        # Organism
        cls.eost = Organism.objects.create(
            name='EOST',
            _type=Organism.OBSERVATORY)
        # Station
        cls.station = StationSite.objects.create(
            site_type=StationSite.SITE_TEST,
            station_code='CHMF',
            operator=cls.eost,
            project=cls.project,
            actor=cls.superuser,
            creation_date='2016-06-10')
        # Network/Channel
        cls.HHZ_code = ChannelCode.objects.create(
            channel_code='HHZ')
        cls.network = Network.objects.create(
            network_code='XX')
        starting_date = datetime.strptime('2016-06-14', '%Y-%m-%d')
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
            start_date=make_aware(starting_date))
        # Equipment
        cls.supertype = EquipSupertype.objects.create(
            equip_supertype_name='01. Scientific',
            presentation_rank='1')
        cls._type = EquipType.objects.create(
            equip_supertype=cls.supertype,
            presentation_rank='1',
            equip_type_name='Datalogger')
        cls.model = EquipModel.objects.create(
            equip_type=cls._type,
            equip_model_name='Centaur')
        # Add parameter to equipment model
        cls.param1 = ParameterEquip.objects.create(
            equip_model=cls.model,
            parameter_name='Number of channels')
        cls.param1value1 = ParameterValue.objects.create(
            parameter=cls.param1,
            value='3',
            default_value=True)
        cls.param1value2 = ParameterValue.objects.create(
            parameter=cls.param1,
            value='6',
            default_value=False)
        cls.param2 = ParameterEquip.objects.create(
            equip_model=cls.model,
            parameter_name='Gain')
        cls.param2value1 = ParameterValue.objects.create(
            parameter=cls.param2,
            value='+10',
            default_value=False)
        cls.param2value2 = ParameterValue.objects.create(
            parameter=cls.param2,
            value='+20',
            default_value=False)
        purchase_date = datetime.strptime('2016-01-01', '%Y-%m-%d')
        cls.equip = Equipment.objects.create(
            equip_model=cls.model,
            serial_number='123456',
            owner=cls.eost,
            stockage_site=cls.station,
            purchase_date=make_aware(purchase_date),
            actor=cls.superuser)

    def login(self):
        self.client.login(
            username=DEFAULT_ADMIN_LOGIN,
            password=DEFAULT_ADMIN_PASSWORD)

    def test_default_configuration_after_equipment_creation(self):
        """
        Check that the equipment have only 1 parameter.
        Check that param1 have its default value.
        """
        config = ConfigEquip.objects.filter(equipment=self.equip)

        # By default: 1 params
        count = len(config)
        self.assertEqual(count, 1, "Wrong parameter count: %s" % count)

        # Param1 should be default value (from model)
        val = self.param1.parametervalue_set.filter(default_value=True).first()
        equip_param1 = ConfigEquip.objects.filter(
            equipment=self.equip,
            parameter=self.param1).first()
        self.assertEqual(
            equip_param1.value,
            val,
            "Wrong value for parameter '%s': %s" % (
                equip_param1.parameter.parameter_name, equip_param1.value))
