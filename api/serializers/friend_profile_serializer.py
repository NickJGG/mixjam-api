from rest_framework import serializers

from api.models import Profile

class FriendProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["tag_line", "color", "picture"]
        extra_kwargs = {}
