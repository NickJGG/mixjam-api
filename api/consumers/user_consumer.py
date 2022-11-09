import json

from channels.generic.websocket import AsyncWebsocketConsumer

from api import models as api_models
from api.controllers import PlaybackController

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.get_user()

        self.room_name = user.username
        self.group_name = "user_%s" % self.room_name

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        user.userprofile.go_online()

    async def disconnect(self, close_code):
        user = self.get_user()

        user.userprofile.go_offline()

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        message = json.loads(text_data)
        user = self.get_user()

        response_message = await PlaybackController(user).handle_message(message)

        await self.group_send(response_message)
    
    async def response(self, message):
        user = self.get_user()

        response_message = await PlaybackController(user).handle_message(message)

        await self.self_send(response_message)

    async def self_send(self, response_data):
        await self.send(text_data=json.dumps(response_data))

    async def group_send(self, data):
        data["type"] = "response"

        await self.channel_layer.group_send(
            self.group_name, data
        )

    async def request_connection(self, data):
        pass

    async def request_playback(self, data):
        pass

    def get_user(self):
        return api_models.User.objects.get(username = self.scope['user'])
