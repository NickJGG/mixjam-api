from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.models import User

from .profile_serializer import ProfileSerializer

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "password", "profile"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True
            },
            "profile": {
                "read_only": True
            }
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )

        Token.objects.create(user = user)

        return user
