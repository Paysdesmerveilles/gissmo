import autocomplete_light.shortcuts as al
from gissmo.models import (
    EquipType,
    EquipModel)


class EquipTypeAutocomplete(al.AutocompleteModelBase):
    search_fields = ['equip_type_name']
    model = EquipType

    attrs = {
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery
        'data-autocomplete-minimum-characters': 1,
    }
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs = {
        'data-widget-maximum-values': 10,
    }


class EquipModelAutocomplete(al.AutocompleteModelBase):
    search_fields = ['equip_model_name']
    model = EquipModel

    attrs = {
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery
        'data-autocomplete-minimum-characters': 2,
    }
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs = {
        'data-widget-maximum-values': 10,
    }

al.register(EquipTypeAutocomplete)
al.register(EquipModelAutocomplete)
