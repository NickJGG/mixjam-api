from api.serializers import PartySerializer

from .base_controller import BaseController
from .playback_controller import PlaybackController

class PartyController(BaseController):
    def __init__(self, user, party):
        super().__init__(user)

        self.party = party
        self.request_actions = {
            "join": self.join,
            "leave": self.leave,
            "get_state": self.get_state
        }
        self.response_actions = {
            "get_state": self.get_state
        }

        party.refresh_from_db()

    async def handle_request(self, message):
        # print(f"REQUEST: { message }")

        data = {
            **message
        }

        action = message.get("action")
        
        if action not in self.request_actions:
            if action not in self.response_actions:
                return await PlaybackController(self.user).handle_request(message)

            return self.create_message(data)

        func = self.request_actions[action]
        data = {
            **data,
            **await func(message),
            "action": "get_state"
        }

        return self.create_message(data)

    async def handle_response(self, message):
        data = {}
        
        action = message.get("action")

        if action not in self.response_actions:
            if action not in self.request_actions:
                return await PlaybackController(self.user).handle_response(message)

            return self.create_message(data)

        func = self.response_actions[action]
        data = {
            **data,
            **await func(message)
        }

        # print(f"RESPONSE: { data }")

        return self.create_message(data)

    async def join(self, message):
        success = self.party.join(self.user)

        return {
            "party": PartySerializer(self.party).data
        }
    
    async def leave(self, message):
        success = self.party.leave(self.user)

        return {
            "party": PartySerializer(self.party).data
        }
    
    async def get_state(self, message):
        return {
            "party": PartySerializer(self.party).data
        }
