from rest_framework import serializers

from api.models import Profile

from .friend_serializer import FriendSerializer

class ProfileSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True)

    class Meta:
        model = Profile
        fields = ["tag_line", "color", "picture", "friends"]
        extra_kwargs = {}
