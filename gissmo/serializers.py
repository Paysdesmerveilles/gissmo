from __future__ import unicode_literals

from gissmo.models import (
    Actor,
    StationSite)

from rest_framework import serializers


class EnumField(serializers.ChoiceField):
    """
    Print choice string instead of its number.
    """
    def to_representation(self, obj):
        res = obj
        for key, value in self.choices.items():
            if key == obj:
                res = value
                break
        return res


class ActorSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='actor_name')
    type = EnumField(choices=Actor.ACTOR_TYPE_CHOICES, source='actor_type')

    class Meta:
        model = Actor
        fields = (
            'id',
            'name',
            'type',
        )


class StationSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='site_name')
    code = serializers.CharField(source='station_code')
    type = EnumField(choices=StationSite.SITE_CHOICES, source='site_type', label='type')
    restricted_status = EnumField(choices=StationSite.STATUS)

    class Meta:
        model = StationSite
        fields = (
            'id',
            'name',
            'code',
            'type',
            'restricted_status',
            'alternate_code',
            'historical_code',
            'latitude_unit',
            'longitude_unit',
            'elevation_unit',
            'longitude',
            'latitude',
            'elevation',
            'town',
            'county',
            'region',
            'country',
            'region',
            # 'vault',  # missing field in station_xml
            'geology',
            'operator',
        )
