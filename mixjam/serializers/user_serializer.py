from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User

from api.models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True
            }
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        profile = Profile.objects.create(
            user = user
        )

        Token.objects.create(user = user)

        return user
