import os
import base64
import json
import requests_async

ENDPOINTS = {
    "refresh": "https://accounts.spotify.com/api/token",

    "player": "https://api.spotify.com/v1/me/player/",
    "play": "https://api.spotify.com/v1/me/player/play",
    "pause": "https://api.spotify.com/v1/me/player/pause",
    "seek": "https://api.spotify.com/v1/me/player/seek",
    "previous": "https://api.spotify.com/v1/me/player/previous",
    "next": "https://api.spotify.com/v1/me/player/next",
    "devices": "https://api.spotify.com/v1/me/player/devices",
    "volume": "https://api.spotify.com/v1/me/player/volume",
    "shuffle": "https://api.spotify.com/v1/me/player/shuffle",
    "repeat": "https://api.spotify.com/v1/me/player/repeat",
    "song": "https://api.spotify.com/v1/me/player/currently-playing",
    "recently_played": "https://api.spotify.com/v1/me/player/recently-played",

    "profile": "https://api.spotify.com/v1/me/",
    "current_user_playlists": "https://api.spotify.com/v1/me/playlists",
    "top_items": "https://api.spotify.com/v1/me/top/",

    "playlist": "https://api.spotify.com/v1/playlists/",
    "artists": "https://api.spotify.com/v1/artists/",

    "recommendations": "https://api.spotify.com/v1/recommendations/",
    "new_releases": "https://api.spotify.com/v1/browse/new-releases",
}

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

class SpotifyClient:
    def __init__(self, user):
        self.user = user

    async def play(self, data):
        return await self.async_put(ENDPOINTS["play"])

    async def pause(self, data):
        return await self.async_put(ENDPOINTS["pause"])

    async def play_direct(self, data):
        pass

    async def play_track(self, data):
        put_data = {
            "uris": [data["track_uri"]]
        }

        return await self.async_put(ENDPOINTS["play"], data = put_data)

    async def play_context(self, data):
        put_data = {}

        if "context_uri" in data:
            put_data["context_uri"] = data["context_uri"]
        
        if "offset" in data:
            put_data["position"] = data["offset"]

        return await self.async_put(ENDPOINTS["play"], data=put_data)

    async def previous(self, data):
        return await self.async_post(ENDPOINTS['previous'])
    
    async def next(self, data):
        return await self.async_post(ENDPOINTS['next'])

    async def seek(self, data):
        put_params = {
            'position_ms': data["progress_ms"]
        }

        return await self.async_put(ENDPOINTS['seek'], params=put_params)

    async def song_end(self, data):
        return await self.get_state(data)

    async def get_state(self, data):
        return await self.async_get(ENDPOINTS["player"])
    
    async def async_refresh_token(self):
        response = await requests_async.post(ENDPOINTS["refresh"], data = {
            "grant_type": "refresh_token",
            "refresh_token": self.user.userprofile.refresh_token
        }, headers = self.get_token_headers())

        r_json = response.json()

        if response.status_code < 400:
            self.user.userprofile.access_token = r_json["access_token"]
            self.user.userprofile.authorized = True
        else:
            self.user.userprofile.authorized = False
        
        self.user.userprofile.save()

        return self.user.userprofile.authorized
    
    def get_client_credentials(self):
        if not CLIENT_SECRET or not CLIENT_ID:
            raise Exception("You must set CLIENT_ID and CLIENT_SECRET")

        client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
        client_creds_b64 = base64.b64encode(client_creds.encode())

        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()

        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.user.userprofile.access_token}"
        }
    
    async def async_get(self, endpoint, params = {}):
        response = await requests_async.get(endpoint, params = params, headers = self.get_headers())

        if response.status_code == 401:
            authorized = await self.async_refresh_token()

            if authorized:
                response = await requests_async.get(endpoint, params = params, headers=self.get_headers())
            else:
                response = {
                    'error': 'unauthorized',
                    'error_message': 'User is unauthorized'
                }

        return response

    async def async_put(self, endpoint, data = {}, params = {}):
        data = json.dumps(data)

        response = await requests_async.put(endpoint, params = params, data = data, headers = self.get_headers())

        if response.status_code == 401:
            authorized = await self.async_refresh_token()

            if authorized:
                response = await requests_async.put(endpoint, params = data, headers = self.get_headers())
            else:
                response = {
                    "error": "unauthorized",
                    "error_message": "User is unauthorized"
                }

        return response

    async def async_post(self, endpoint, data = {}):
        data = json.dumps(data)

        response = await requests_async.post(endpoint, data = data, headers = self.get_headers())

        if response.status_code == 401:
            authorized = await self.async_refresh_token()

            if authorized:
                response = await requests_async.post(endpoint, data = data, headers = self.get_headers())
            else:
                response = {
                    'error': 'unauthorized',
                    'error_message': 'User is unauthorized'
                }

        return response
