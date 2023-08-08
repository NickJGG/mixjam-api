from django.db import models
from django.contrib.auth.models import User

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

class Party(models.Model):
    code = models.CharField(primary_key=True, max_length=30, default="default")
    mode = models.CharField(max_length=50, choices=PartyMode.MODE_CHOICES, default=PartyMode.PRIVATE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    users = models.ManyToManyField(User, blank=True, related_name="party_users")
    allowed_users = models.ManyToManyField(User, blank=True, related_name="party_allowed_users")

    invite_code = models.CharField(max_length = 6, null=True, blank=True)
    invite_time = models.DateTimeField(blank=True, null=True)
    
    context_uri = models.CharField(max_length=255, blank=True, null=True)
    track_uri = models.CharField(max_length=255, blank=True, null=True)
    track_index = models.IntegerField(default=0, blank=True)
    track_progress_ms = models.IntegerField(default=0, null=True, blank=True)
    playback_last_action = models.DateTimeField(null=True, blank=True)
    track_last_end = models.DateTimeField(null=True, blank=True)
    playing = models.BooleanField(default=False, blank=True)

    time_created = models.DateTimeField(auto_now_add=True, null=True)

    def join(self, user):
        if not self.user_can_join(user):
            return False
        
        self.users.add(user)
        self.save()

        user.profile.party = self
        user.profile.save()

        return True
    
    def leave(self, user):
        self.users.remove(user)
        self.save()

        user.profile.party = None
        user.profile.save()

        return True

    def can_invite(self, sender, receiver):
        self.refresh_from_db()

        print("sender party:", sender.profile.party)
        print("in current party?:", sender.profile.party == self)
        print("is friend:", sender.profile.friends.filter(id=receiver.id).exists())
        print("can invite?:", sender.profile.party == self and sender.profile.friends.filter(id=receiver.id).exists())

        if sender.profile.party == self and sender.profile.friends.filter(id=receiver.id).exists():
            return True
        
        return False

    def user_can_join(self, user):
        return True
