from rest_framework import serializers

from api.models import Notification

from .user_serializer import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Notification
        fields = "__all__"
