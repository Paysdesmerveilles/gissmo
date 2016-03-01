from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from intervention.models import (
    ActionEquipment,
    ActionSite,
    Intervention,
    InterventionPlayer)

from intervention.forms import InterventionForm

from user.models import Player


class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'players'


class UserAdmin(UserAdmin):
    inlines = (PlayerInline, )


class InterventionPlayer(admin.TabularInline):
    model = InterventionPlayer
    extra = 1

class ActionEquipmentInline(admin.TabularInline):
    model = ActionEquipment
    extra = 0


class ActionSiteInline(admin.TabularInline):
    model = ActionSite
    extra = 0


class InterventionAdmin(admin.ModelAdmin):
    fields = ['site', 'date', 'note']
    list_display = ['date', 'site']
    inlines = [InterventionPlayer, ActionSiteInline, ActionEquipmentInline]
    form = InterventionForm

    class Media:
        js = ["/static/intervention/admin/pageadmin.js"]


# Players
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Player)

# Intervention
admin.site.register(Intervention, InterventionAdmin)
