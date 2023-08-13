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

        self.client = SpotifyClient(self.user)
        self.party = party
        self.party_actions = {
            PartyAction.JOIN: self.join,
            PartyAction.LEAVE: self.leave,
            PartyAction.GET_STATE: self.get_state,
        }
        self.playback_actions = {
            PlaybackAction.PLAY: self.party.play,
            PlaybackAction.PAUSE: self.party.pause,
            PlaybackAction.NEXT: self.party.next,
            PlaybackAction.PREVIOUS: self.party.previous,
            PlaybackAction.PLAY_TRACK: self.party.play_track,
            PlaybackAction.PLAY_CONTEXT: self.party.play_context,
        }
        self.response_actions = {
            "get_state": self.get_state,
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
            response = await PlaybackController(self.user).handle_response(response)

            if action not in PlaybackAction.REQUIRES_NO_SYNC:
                await self.partial_sync()

            return response

        func = self.response_actions[action]
        data = {
            **data,
            **await func(response),
        }

        return self.create_message(data)

    #region PLAYBACK REQUESTS

    async def handle_playback_request(self, request):
        action = request.get("action")
        party_action = self.playback_actions.get(action, None)
        
        if party_action is not None:
            party_action(request)

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
            await self.full_sync()

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
            "party": PartySerializer(self.party).data,
        }

    async def partial_sync(self):
        await self.client.async_seek({
            "progress_ms": self.party.current_track_progress(),
        })

    async def full_sync(self):
        data = {
            "track_uri": self.party.track_uri,
        }

        if self.party.context_uri is None:
            if self.party.track_uri is not None:
                await self.client.play_track(data)
        else:
            await self.client.play_context({
                **data,
                "context_uri": self.party.context_uri,
            })
        
        if not self.party.playing:
            self.client.pause({})

        await self.client.async_seek({
            "progress_ms": self.party.current_track_progress(),
        })
