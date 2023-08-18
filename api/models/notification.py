from django.db import models
from django.contrib.auth.models import User

class NotificationAction:
    ACCEPT = "accept"
    IGNORE = "ignore"

class NotificationType:
    FRIEND_REQUEST = "friendrequest"
    PARTY_INVITE = "partyinvite"

    MATCH = {
        FRIEND_REQUEST: FRIEND_REQUEST,
        PARTY_INVITE: PARTY_INVITE,
    }

class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")

    time_sent = models.DateTimeField(auto_now_add=True)
