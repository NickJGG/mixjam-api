import os

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string

class RoomMode:
    PUBLIC = "public"
    PRIVATE = "private"
    CLOSED = "closed"

    MODE_CHOICES = [
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
        (CLOSED, "Closed"),
    ]

class Room(models.Model):
    code = models.CharField(primary_key = True, max_length = 30, default = "default")
    title = models.CharField(max_length = 150, default = "New Room")
    description = models.CharField(max_length = 1000, default = "")
    banner_color = models.CharField(max_length = 6, null = True, blank = True, default = "ec4a4e")
    mode = models.CharField(max_length = 50, choices = RoomMode.MODE_CHOICES, default = RoomMode.PRIVATE)

    invite_code = models.CharField(max_length = 6, null = True, blank = True)
    invite_time = models.DateTimeField(blank = True, null = True)

    creator = models.ForeignKey(User, on_delete = models.CASCADE)
    time_created = models.DateTimeField(auto_now_add = True, null = True)

    playlist_id = models.CharField(max_length = 50, null = True)
    playlist_image_url = models.CharField(max_length = 250, null = True, blank = True)

    users = models.ManyToManyField(User, blank = True, related_name = "users")
    active_users = models.ManyToManyField(User, blank = True, related_name = "active_users")
    inactive_users = models.ManyToManyField(User, blank = True, related_name = "inactive_users")

    def __str__(self):
        return self.code

    def is_active(self):
        return self.active_users.count() > 0
    
    def others_active(self, user):
        return (self.active_users.count() - 1 if user in self.active_users.all() else 0) > 0
    
    def get_site_url(self):
        return "http://localhost:3000" if os.environ.get(
            "DJANGO_DEVELOPMENT") else "https://mixjam.io"

    def get_invite_link(self):
        self.check_invite()

        return self.get_site_url() + reverse("invite", kwargs = {
            "invite_code": self.invite_code
        })

    def new_invite(self):
        self.invite_code = get_random_string(length=6)
        self.invite_time = timezone.now()

        self.save()

    def check_invite(self):
        if self.mode == RoomMode.PUBLIC:
            return True
        elif self.invite_time is not None and (timezone.now() - self.invite_time).total_seconds() / 3600 < 24:
            return True
        else:
            self.new_invite()
        
        return False
