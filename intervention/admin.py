from django.contrib import admin

from intervention.models import Intervention


class InterventionAdmin(admin.ModelAdmin):
    fields = ['place', 'date', 'confirmed', 'note']
    list_display = ('date', 'place', 'confirmed')
    search_fields = ['date', 'place__name']

    # TODO: Create an action "Confirm selected interventions"
    # TODO: Create an action "Merge selected interventions"


admin.site.register(Intervention, InterventionAdmin)
