from api.models import Party
from api.serializers import PartySerializer

from .base_controller import BaseController
from .playback_controller import PlaybackController

class UserController(BaseController):
    def __init__(self, user):
        super().__init__(user)

        self.actions = {
            "join_party": self.join_party
        }
        self.allowed_types = [
            "notification"
        ]

    async def handle_request(self, message):
        # print(f"REQUEST: { message }")

        data = {
            **message
        }

        action = message.get("action")

        if action not in self.actions:
            return await PlaybackController(self.user).handle_request(message)

        return self.create_message(data)
    
    async def handle_response(self, message):
        data = {}
        
        action = message.get("action")

        if action is None:
            type =  message.get("type")

            if type in self.allowed_types:
                data = {
                    **data,
                    **message
                }
        elif action in self.actions:
            func = self.actions[action]
            data = {
                **data,
                **await func(message)
            }
        else:
            return await PlaybackController(self.user).handle_response(message)

        print(f"RESPONSE: { data }")

        return self.create_message(data)
    
    async def join_party(self, message):
        data = {
            "joined": False
        }

        party_code = message.get("party_code", "")

        party = Party.objects.filter(code=party_code)

        if party.exists():
            party = party.first()
            can_join = party.user_can_join(self.user)

            data["join_party"] = can_join

            if can_join:
                data["party"] = PartySerializer(party).data

        return data
