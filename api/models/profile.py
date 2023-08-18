from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
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
        self.party = None

        self.save()

        return self.online_count
    
    def can_party_invite(self, user_id, party_code):
        self.refresh_from_db()

        print(self.party.code, party_code)

        print(self.friends.filter(id=user_id).exists())
        print(self.party is not None and self.party.code == party_code)

        if self.friends.filter(id=user_id).exists() and self.party is not None and self.party.code == party_code:
            return True
        
        return False
