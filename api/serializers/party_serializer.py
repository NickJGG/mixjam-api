from rest_framework import serializers

from api.models import Party

from .friend_serializer import FriendSerializer
from .user_serializer import UserSerializer

class PartySerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True)
    creator = FriendSerializer()

    class Meta:
        model = Party
        fields = "__all__"
