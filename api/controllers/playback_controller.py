from asgiref.sync import async_to_sync

from api import SpotifyClient

from .base_controller import BaseController

class PlaybackAction:
    GET_STATE = "get_state"
    PLAY = "play"
    PLAY_DIRECT = "play_direct"
    PLAY_CONTEXT = "play_context"
    PLAY_TRACK = "play_track"
    PAUSE = "pause"
    PREVIOUS = "previous"
    NEXT = "next"
    SEEK = "seek"
    TRACK_END = "track_end"
    ADD_QUEUE = "add_queue"

    ALL = [
        PLAY,
        PLAY_DIRECT,
        PLAY_CONTEXT,
        PLAY_TRACK,
        PAUSE,
        PREVIOUS,
        NEXT,
        SEEK,
        TRACK_END,
        ADD_QUEUE
    ]

    REQUIRES_NO_SYNC = [
        ADD_QUEUE,
    ]

class PlaybackController(BaseController):
    def __init__(self, user):
        super().__init__(user)

        self.spotify = SpotifyClient(user)
        self.spotify_actions = {
            PlaybackAction.GET_STATE: self.spotify.get_state_async,
            PlaybackAction.PLAY: self.spotify.play,
            PlaybackAction.PLAY_DIRECT: self.spotify.play_direct,
            PlaybackAction.PLAY_CONTEXT: self.spotify.play_context,
            PlaybackAction.PLAY_TRACK: self.spotify.play_track,
            PlaybackAction.PAUSE: self.spotify.pause,
            PlaybackAction.PREVIOUS: self.spotify.previous,
            PlaybackAction.NEXT: self.spotify.next,
            PlaybackAction.SEEK: self.spotify.async_seek,
            PlaybackAction.TRACK_END: self.spotify.track_end,
            PlaybackAction.ADD_QUEUE: self.spotify.add_queue,
        }
    
    async def handle_request(self, message):
        print(f"[Playback] Request: { message }")

        data = {
            **message
        }

        return self.create_message(data)
    
    async def handle_response(self, message, get_state=False):
        print(f"[Playback] Response: { message }")

        data = {}

        action = message.get("action")

        func = self.spotify_actions.get(action)
        action_result = await func(message)
        
        if get_state:
            playback_state = await self.spotify.get_state_async(action_result)

            try:
                data["playback"] = playback_state
            except:
                pass

        return self.create_message(data)
