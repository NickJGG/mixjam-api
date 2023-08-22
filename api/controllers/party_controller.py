from copy import deepcopy

from api.spotify_client import SpotifyClient
from api.serializers import PartySerializer

from .base_controller import BaseController
from .playback_controller import PlaybackController, PlaybackAction

class PartyAction:
    JOIN = "join"
    LEAVE = "leave"
    DISCONNECT = "disconnect"
    GET_STATE = "get_state"

    ALL = [
        JOIN,
        LEAVE,
        DISCONNECT,
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
            PartyAction.DISCONNECT: self.disconnect,
            PartyAction.GET_STATE: self.get_state,
        }
        self.playback_actions = {
            PlaybackAction.PLAY: self.party.play,
            PlaybackAction.PAUSE: self.party.pause,
            PlaybackAction.NEXT: self.party.next,
            PlaybackAction.PREVIOUS: self.party.previous,
            PlaybackAction.PLAY_TRACK: self.party.play_track,
            PlaybackAction.PLAY_CONTEXT: self.party.play_context,
            PlaybackAction.SEEK: self.party.seek,
            PlaybackAction.TRACK_END: self.party.track_end,
        }
        self.response_actions = {
            "track_end": self.get_state,
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

        action = response.get("action")
        current_state = None
        #update_party_uris = action == PlaybackAction.TRACK_END and self.party.track_ending and self.party.track_ender == self.user

        if action in PlaybackAction.ALL:
            playback_response = await PlaybackController(self.user).handle_response(response, get_state=True)

            response = {
                **response,
                **playback_response["data"],
            }

            if action not in PlaybackAction.REQUIRES_NO_SYNC:
                await self.partial_sync()
        
        if action != PlaybackAction.GET_STATE and current_state is None:
            playback_state = await self.client.get_state_async({})

            response = {
                **response,
                **playback_state,
            }

        if action in self.response_actions:
            func = self.response_actions[action]
            response = {
                **response,
                **await func(response),
            }

        return self.create_message(response)

    #region PLAYBACK REQUESTS

    async def handle_playback_request(self, request):
        action = request.get("action")
        party_action = self.playback_actions.get(action, None)
        
        party_request = deepcopy(request)

        if action == PlaybackAction.TRACK_END:
            party_request["track_ender"] = self.user

        if party_action is not None:
            party_response = party_action(party_request)

            print(party_response)

            if action == PlaybackAction.TRACK_END and "respond" in party_response:
                respond = party_response["respond"]

                request["respond"] = respond

                if respond:
                    current_state = self.client.get_state({})

                    track_uri = current_state.get("item").get("uri")

                    self.party.play_track({
                        "track_uri": track_uri,
                    })

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

        return await self.get_state(message)
    
    async def leave(self, message):
        success = self.party.leave(self.user)

        return await self.get_state(message)

    async def disconnect(self, message):
        success = self.party.disconnect(self.user)

        return await self.get_state(message)
    
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
        
        if self.party.playing:
            self.client.play({})
        else:
            self.client.pause({})

        await self.client.async_seek({
            "progress_ms": self.party.current_track_progress(),
        })
