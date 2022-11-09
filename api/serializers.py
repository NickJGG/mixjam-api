from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.fields import CurrentUserDefault

from django.contrib.auth.models import User

from .models import *

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['tag_line', 'color', 'picture']
        extra_kwargs = {}

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'userprofile']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True
            },
            'userprofile': {
                'read_only': True
            }
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        Token.objects.create(user = user)

        return user

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    playlist = PlaylistSerializer()
    creator = UserSerializer()

    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['code', 'creator']
    
    def create(self, validated_data):
        code = self.generate_code()

        room = Room.objects.create(code = code, creator = self.context['request'].user, **validated_data)

        return room
    
    def generate_code(self):
        while True:
            new_code = get_random_string(length = 6)

            rooms = Room.objects.filter(code = new_code)

            if not rooms.exists():
                break
        
        return new_code