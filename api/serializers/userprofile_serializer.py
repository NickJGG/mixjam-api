from rest_framework import serializers

from api.models import UserProfile

from .friend_serializer import FriendSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ["tag_line", "color", "picture", "friends"]
        extra_kwargs = {}
