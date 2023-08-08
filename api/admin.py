from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Profile)
admin.site.register(Room)
admin.site.register(Playlist)
admin.site.register(Party)
admin.site.register(Notification)
admin.site.register(PartyInvite)