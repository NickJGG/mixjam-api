import os
from channels.db import DatabaseSyncToAsync

from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.urls import reverse

from . import util

class PartyMode(models.Model):
    PUBLIC = "public"
    FRIENDS_ONLY = "friendsonly"
    PRIVATE = "private"
    CLOSED = "closed"

    MODE_CHOICES = [
        (PUBLIC, "Public"),
        (FRIENDS_ONLY, "Friends Only"),
        (PRIVATE, "Private"),
        (CLOSED, "Closed"),
    ]

class NotificationAction(models.Model):
    ACCEPT = "accept"
    IGNORE = "ignore"

class NotificationType(models.Model):
    FRIEND_REQUEST = "friendrequest"
    PARTY_INVITE = "partyinvite"

class RoomMode(models.Model):
    PUBLIC = "public"
    PRIVATE = "private"
    CLOSED = "closed"

    MODE_CHOICES = [
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
        (CLOSED, "Closed"),
    ]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    spotify_username = models.CharField(max_length = 50, blank = True, null = True)
    tag_line = models.CharField(max_length = 50, default = "Jammer")
    access_token = models.CharField(max_length = 210, blank = True, null = True)
    refresh_token = models.CharField(max_length = 210, blank = True, null = True)
    authorized = models.BooleanField(default = False)
    party = models.ForeignKey("Party", blank = True, null = True, on_delete = models.SET_NULL, related_name = "user_party")
    friends = models.ManyToManyField(User, blank = True, related_name = "friends")

    color = models.CharField(max_length = 6, default = "1c71ca")

    picture = models.CharField(max_length = 100, blank = True, null = True)

    new_user = models.BooleanField(default = True)

    online_count = models.IntegerField(default = 0, blank = True)

    def __str__(self):
        return self.user.username

    def go_online(self):
        self.online_count += 1
        self.save()

        return self.online_count
    
    def go_offline(self):
        self.online_count = self.online_count - 1 if self.online_count > 0 else 0
        self.save()

        return self.online_count

class Party(models.Model):
    code = models.CharField(primary_key = True, max_length = 30, default = "default")
    mode = models.CharField(max_length = 50, choices = PartyMode.MODE_CHOICES, default = PartyMode.PRIVATE)
    creator = models.ForeignKey(User, on_delete = models.CASCADE)

    users = models.ManyToManyField(User, blank = True, related_name = "party_users")
    allowed_users = models.ManyToManyField(User, blank = True, related_name = "party_allowed_users")

    invite_code = models.CharField(max_length = 6, null = True, blank = True)
    invite_time = models.DateTimeField(blank = True, null = True)
    
    song_index = models.IntegerField(default = 0, blank = True)
    progress_ms = models.IntegerField(default = 0, null = True, blank = True)
    last_action = models.DateTimeField(null = True, blank = True)
    last_song_end = models.DateTimeField(null = True, blank = True)
    playing = models.BooleanField(default = False, blank = True)

    time_created = models.DateTimeField(auto_now_add = True, null = True)

    def join(self, user):
        if not self.user_can_join(user):
            return False
        
        self.users.add(user)
        self.save()

        return True
    
    def leave(self, user):
        print(self.users.all())
        self.users.remove(user)
        self.save()
        print(self.users.all())

        return True

    def save(self, *args, **kwargs):
        print("save")
        super(Party, self).save(*args, **kwargs)

    def user_can_join(self, user):
        return True

class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")

    time_sent = models.DateTimeField(auto_now_add=True)

class PartyInvite(models.Model):
    notification = models.ForeignKey("Notification", on_delete=models.CASCADE)
    party = models.ForeignKey("Party", on_delete=models.CASCADE)

    def get_available_actions(self):
        return [NotificationAction.ACCEPT, NotificationAction.IGNORE]

    def get_type(self):
        return NotificationType.PARTY_INVITE

    def can_perform_action(self, action):
        if action == NotificationAction.IGNORE:
            return True, ""
        
        if self.party.mode == PartyMode.PUBLIC:
            return True, ""
        
        return True, ""
    
    def perform_action(self, action):
        can_perform_action, message = self.can_perform_action(action)

        if not can_perform_action:
            return {
                "success": False,
                "message": f"Unable to { action }: { message }"
            }
        
        print(action)

        if action == NotificationAction.ACCEPT:
            self.party.allowed_users.add(self.notification.receiver)
            print(self.party.allowed_users.all())
            self.party.save()
        
        return {
            "success": True
        }


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

class Playlist(models.Model):
    room = models.OneToOneField(Room, on_delete = models.CASCADE)
    song_index = models.IntegerField(default = 0, blank = True)
    progress_ms = models.IntegerField(default = 0, null = True, blank = True)
    last_action = models.DateTimeField(null = True, blank = True)
    last_song_end = models.DateTimeField(null = True, blank = True)
    playing = models.BooleanField(default = False, blank = True)

    def get_progress(self, user):
        if self.playing:
            progress_ms = util.get_adjusted_progress(self.room)
        else:
            progress_ms = self.progress_ms

        return progress_ms

    def song_end(self):
        now = timezone.now()

        if self.last_song_end is None or (now - self.last_song_end).total_seconds() > 5:
            self.last_song_end = now
            self.save()

            self.next_song()

            return True
        
        return False

    def previous_song(self):
        self.song_index = self.song_index - 1 if self.song_index > 0 else 0
        self.progress_ms = 0
        self.save()
    
    def next_song(self):
        self.song_index += 1
        self.progress_ms = 0
        self.save()

    @DatabaseSyncToAsync
    def restart(self):
        self.song_index = 0
        self.progress_ms = 0
        self.save()