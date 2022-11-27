from rest_framework import serializers

from api.models import Party

from .user_serializer import UserSerializer

class PartySerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Party
        fields = "__all__"
