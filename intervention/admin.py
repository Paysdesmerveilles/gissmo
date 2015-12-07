from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from intervention.models import Player

class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'players'

class UserAdmin(UserAdmin):
    inlines = (PlayerInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
