from rest_framework import serializers

from api.models import User

from .friend_profile_serializer import FriendProfileSerializer

class FriendSerializer(serializers.ModelSerializer):
    profile = FriendProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "profile"]
