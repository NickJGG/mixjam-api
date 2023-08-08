from django.db import models

from .notification import NotificationAction, NotificationType

class FriendRequest(models.Model):
    notification = models.ForeignKey("Notification", on_delete=models.CASCADE)

    def get_available_actions(self):
        return [NotificationAction.ACCEPT, NotificationAction.IGNORE]

    def get_type(self):
        return NotificationType.FRIEND_REQUEST

    def can_perform_action(self, action):
        if action == NotificationAction.IGNORE:
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
            self.notification.receiver.friends.add(self.notification.sender)
            self.notification.receiver.save()

            self.notification.sender.friends.add(self.notification.receiver)
            self.notification.sender.save()

            self.notification.delete()
        
        return {
            "success": True
        }
