from __future__ import unicode_literals

from gissmo.models import StationSite

from rest_framework import serializers


class StationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StationSite
        fields = (
            'station_code',
            'site_name',
            'site_description',
            'latitude',
            'longitude',
            'elevation',
            'site_type',
            'station_parent',
        )
