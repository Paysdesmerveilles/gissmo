from django.contrib import admin

from intervention.models import Intervention


class InterventionAdmin(admin.ModelAdmin):
    fields = ['site', 'date', 'confirmed']
    list_display = ('date', 'site', 'confirmed')
    search_fields = ['date', 'site__name']

    # TODO: Create an action "Confirm selected interventions"
    # TODO: Create an action "Merge selected interventions"


admin.site.register(Intervention, InterventionAdmin)
