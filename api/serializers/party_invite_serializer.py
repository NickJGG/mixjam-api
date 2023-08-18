from rest_framework import serializers

from api.models import PartyInvite

from .notification_serializer import NotificationSerializer

class PartyInviteSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer()
    available_actions = serializers.ListField(source="get_available_actions")
    type = serializers.CharField(source="get_type")

    class Meta:
        model = PartyInvite
        fields = "__all__"