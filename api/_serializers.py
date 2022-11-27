# class PlaylistSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Playlist
#         fields = "__all__"

# class RoomSerializer(serializers.ModelSerializer):
#     playlist = PlaylistSerializer()
#     creator = UserSerializer()

#     class Meta:
#         model = Room
#         fields = "__all__"
#         read_only_fields = ["code", "creator"]
    
#     def create(self, validated_data):
#         code = self.generate_code()

#         room = Room.objects.create(code = code, creator = self.context["request"].user, **validated_data)

#         return room
    
#     def generate_code(self):
#         while True:
#             new_code = get_random_string(length = 6)

#             rooms = Room.objects.filter(code = new_code)

#             if not rooms.exists():
#                 break
        
#         return new_code
