from django.db import models

from .notification import NotificationAction, NotificationType
from .party import PartyMode

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

        if action == NotificationAction.ACCEPT:
            self.party.allowed_users.add(self.notification.receiver)
            self.party.save()

            self.notification.receiver.profile.party = self.party
            self.notification.receiver.profile.save()

        self.notification.delete()
        self.delete()
        
        return {
            "success": True
        }
