from api import SpotifyClient

from .base_controller import BaseController
class PlaybackController(BaseController):
    def __init__(self, user):
        super().__init__(user)

        self.spotify = SpotifyClient(user)
        self.spotify_actions = {
            'get_state': self.spotify.get_state,
            'play': self.spotify.play,
            'play_direct': self.spotify.play_direct,
            'play_context': self.spotify.play_context,
            'play_track': self.spotify.play_track,
            'pause': self.spotify.pause,
            'previous': self.spotify.previous,
            'next': self.spotify.next,
            'seek': self.spotify.seek,
            "song_end": self.spotify.song_end
        }
    
    async def handle_request(self, message):
        print(f"REQUEST: { message }")

        data = {
            **message
        }

        return self.create_message(data)
    
    async def handle_response(self, message):
        print(f"RESPONSE: { message }")

        data = {}

        action = message.get("action")

        func = self.spotify_actions[action]
        action_result = await func(message)

        playback_state = await self.spotify.get_state(action_result)

        try:
            data["playback"] = playback_state.json()
        except:
            pass

        return self.create_message(data)
