from rest_framework import serializers

from api.models import UserProfile

class FriendProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["tag_line", "color", "picture"]
        extra_kwargs = {}
