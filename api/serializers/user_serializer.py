from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.models import User

from .userprofile_serializer import UserProfileSerializer

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "password", "userprofile"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True
            },
            "userprofile": {
                "read_only": True
            }
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        Token.objects.create(user = user)

        return user
