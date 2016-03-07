from django.contrib import admin
from django.contrib.auth.models import User

from user.models import (
    GissmoUser,
    Player)

# Players
admin.site.unregister(User)
admin.site.register(GissmoUser)
admin.site.register(Player)
