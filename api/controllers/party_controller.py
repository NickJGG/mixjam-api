from api.spotify_client import SpotifyClient
from api.serializers import PartySerializer

from .base_controller import BaseController
from .playback_controller import PlaybackController, PlaybackAction

class PartyAction:
    JOIN = "join"
    LEAVE = "leave"
    GET_STATE = "get_state"

    ALL = [
        JOIN,
        LEAVE,
        GET_STATE,
    ]

class PartyController(BaseController):
    def __init__(self, user, party):
        super().__init__(user)

        self.party = party
        self.party_actions = {
            PartyAction.JOIN: self.join,
            PartyAction.LEAVE: self.leave,
            PartyAction.GET_STATE: self.get_state,
        }
        self.response_actions = {
            "get_state": self.get_state
        }

        party.refresh_from_db()

    async def handle_request(self, request):
        print(f"[Party][Request] { self.user.username }: { request }")

        action = request.get("action")
        
        if action in PlaybackAction.ALL:
            return await self.handle_playback_request(request)
        
        if action in PartyAction.ALL:
            return await self.handle_party_request(request)

        return self.create_message(request)

    async def handle_response(self, response):
        print(f"[Party][Response] { self.user.username }: { response }")

        data = {}

        action = response.get("action")

        if action in PlaybackAction.ALL:
            return await PlaybackController(self.user).handle_response(response)

        func = self.response_actions[action]
        data = {
            **data,
            **await func(response)
        }

        return self.create_message(data)

    #region PLAYBACK REQUESTS

    async def handle_playback_request(self, request):
        action = request.get("action")

        track_uri = request.get("track_uri", None)
        context_uri = request.get("context_uri", None)

        if track_uri is not None:
            self.party.track_uri = track_uri

        if context_uri is not None:
            self.party.context_uri = context_uri

        self.party.save()

        return await PlaybackController(self.user).handle_request(request)

    #endregion


    #region PARTY REQUESTS

    async def handle_party_request(self, request):
        action = request.get("action")

        func = self.party_actions[action]
        request = {
            **request,
            **await func(request),
            "action": "get_state"
        }

        return self.create_message(request)

    async def join(self, message):
        success = self.party.join(self.user)

        if success and self.party.users.count() > 1:
            await self.sync()

        return {
            "party": PartySerializer(self.party).data
        }
    
    async def leave(self, message):
        success = self.party.leave(self.user)

        return {
            "party": PartySerializer(self.party).data
        }
    
    #endregion
    
    async def get_state(self, message):
        return {
            "party": PartySerializer(self.party).data
        }

    async def sync(self):
        client = SpotifyClient(self.user)
    
        data = {
            "track_uri": self.party.track_uri,
        }

        if self.party.context_uri is None:
            if self.party.track_uri is not None:
                await client.play_track(data)
        else:
            await client.play_context({
                **data,
                "context_uri": self.party.context_uri,
            })
