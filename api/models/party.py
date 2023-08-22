from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")

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
    track_ending = models.BooleanField(default=False, blank=True)
    track_ender = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING, related_name="track_ender")

    time_created = models.DateTimeField(auto_now_add=True, null=True)

    def num_users_online(self):
        print(list(map(lambda user: user.profile.online_count, self.users.all())))

        return len(list(filter(lambda user: user.profile.online_count > 0, self.users.all())))

    def join(self, user):
        if not self.user_can_join(user):
            return False
        
        self.users.add(user)
        self.save()

        user.profile.party = self
        user.profile.save()

        return True
    
    def leave(self, user):
        print("\n\n\n\n\nLEAVE\n\n\n\n\n")

        self.disconnect(user)

        user.profile.party = None
        user.profile.save()

        return True

    def disconnect(self, user):
        self.users.remove(user)
        self.save()

        if self.users.count() == 0:
            for user in self.allowed_users.all():
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

    def play(self, args):
        self.playing = True
        self.playback_last_action = timezone.now()
        self.save()

    def play_track(self, args):
        self.track_uri = args.get("track_uri")
        self.context_uri = args.get("context_uri", self.context_uri)
        self.end_track(args)

    def play_context(self, args):
        self.context_uri = args.get("context_uri")
        self.end_track(args)
    
    def pause(self, args):
        self.track_progress_ms = self.current_track_progress()
        self.playing = False
        self.playback_last_action = timezone.now()
        self.save()
    
    def previous(self, args):
        self.track_index = self.track_index - 1 if self.track_index > 0 else 0
        self.end_track(args)

    def next(self, args):
        self.track_index += 1
        self.end_track(args)

    def end_track(self, args):
        self.track_ending = False
        self.track_progress_ms = 0
        self.track_ender = None
        self.play(args)

    def track_end(self, args):
        if self.track_ending:
            return {
                "respond": False,
            }

        ending_track_uri = args.get("track_uri")
        track_ender = args.get("track_ender")

        if self.track_uri == ending_track_uri:
            self.track_ending = True
            self.track_ender = track_ender
            self.save()

            return {
                "respond": True,
            }

        return {
            "respond": False,
        }

    def seek(self, args):
        self.track_progress_ms = args.get("progress_ms")
        self.play(args)

    def current_track_progress(self):
        if not self.playing:
            return self.track_progress_ms

        since_last_playback_action_ms = round((timezone.now() - self.playback_last_action).total_seconds() * 1000)
        current_track_progress_ms = self.track_progress_ms + since_last_playback_action_ms

        return current_track_progress_ms
