import json

from channels.generic.websocket import AsyncWebsocketConsumer

from api import models as api_models
from api.controllers import UserController

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

        print(user.profile.party)

        if user.profile.party is not None and user.profile.party.num_users_online() > 0:
            request = json.dumps({
                "type": "request",
                "data": {
                    "action": "join_party",
                    "party_code": user.profile.party.code,
                }
            })
            await self.receive(request)
        else:
            user.profile.party = None
            user.profile.save()

        user.profile.go_online()

    async def disconnect(self, close_code):
        user = self.get_user()

        user.profile.go_offline()

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        message = json.loads(text_data)
        user = self.get_user()

        response_message = await UserController(user).handle_message(message)

        await self.group_send(response_message)
    
    async def response(self, message):
        user = self.get_user()

        response_message = await UserController(user).handle_message(message)

        await self.self_send(response_message)

    async def self_send(self, response_data):
        await self.send(text_data=json.dumps(response_data))

    async def group_send(self, data):
        data["type"] = "response"

        await self.channel_layer.group_send(
            self.group_name, data
        )

    def get_user(self):
        return api_models.User.objects.get(username = self.scope['user'])
