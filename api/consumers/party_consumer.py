import json

from channels.generic.websocket import AsyncWebsocketConsumer

from api import models as api_models
from api.controllers import PartyController

class PartyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        party_code = self.scope['url_route']['kwargs']['party_code']

        self.room_name = party_code
        self.group_name = f"party_{ self.room_name }"

        party = self.get_party()
        user = self.get_user()

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        request = json.dumps({
            "type": "request",
            "data": {
                "action": "join"
            }
        })
        await self.receive(request)

    async def disconnect(self, close_code):
        request = json.dumps({
            "type": "request",
            "data": {
                "action": "disconnect"
            }
        })
        await self.receive(request)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        message = json.loads(text_data)
        user = self.get_user()
        party = self.get_party()

        response_message = await PartyController(user, party).handle_message(message)

        await self.group_send(response_message)
    
    async def response(self, message):
        user = self.get_user()
        party = self.get_party()

        response_message = await PartyController(user, party).handle_message(message)

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

    def get_party(self):
        return api_models.Party.objects.get(code = self.room_name)
