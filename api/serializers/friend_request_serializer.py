from rest_framework import serializers

from api.models import FriendRequest

from .notification_serializer import NotificationSerializer

class FriendRequestSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer()
    available_actions = serializers.ListField(source="get_available_actions")
    type = serializers.CharField(source="get_type")

    class Meta:
        model = FriendRequest
        fields = "__all__"