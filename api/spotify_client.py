import os
import base64
import json
import requests_async
import requests

import time

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
    "saved_tracks": "https://api.spotify.com/v1/me/tracks",

    "profile": "https://api.spotify.com/v1/me/",
    "current_user_playlists": "https://api.spotify.com/v1/me/playlists",
    "top_items": "https://api.spotify.com/v1/me/top/{type}",

    "playlist": "https://api.spotify.com/v1/playlists/",
    "artists": "https://api.spotify.com/v1/artists/",

    "recommendations": "https://api.spotify.com/v1/recommendations/",
    "related_artists": "https://api.spotify.com/v1/artists/{artist_id}/related-artists",
    "new_releases": "https://api.spotify.com/v1/browse/new-releases",
    "search": "https://api.spotify.com/v1/search",

    "saved_tracks": "https://api.spotify.com/v1/me/tracks",
    "saved_artists": "https://api.spotify.com/v1/me/following/",
    "saved_albums": "https://api.spotify.com/v1/me/albums",
    "saved_playlists": "https://api.spotify.com/v1/users/{user_id}/playlists",

    "track_is_saved": "https://api.spotify.com/v1/me/tracks/contains/",
    "artist_is_saved": "https://api.spotify.com/v1/me/following/contains/",
    "album_is_saved": "https://api.spotify.com/v1/me/albums/contains/",
    "playlist_is_saved": "https://api.spotify.com/v1/playlists/{playlist_id}/followers/contains/",
    "tracks_save": "https://api.spotify.com/v1/me/tracks",
    "albums_save": "https://api.spotify.com/v1/me/albums",
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
        time.sleep(.25)
        return await self.async_get(ENDPOINTS["player"])
    
    def save(self, data):
        type = data.pop("type")
        save = data.pop("save")

        if save:
            func = self.put
        else:
            func = self.delete

        return func(ENDPOINTS[f"{ type }_save"], params=data)

    def check_if_saved(self, data):
        type = data.get('type')

        endpoint = ENDPOINTS[f"{ type }_is_saved"]

        if type == "playlist":
            ids = data["ids"].split(",")
            save_checks = []

            for id in ids:
                endpoint = endpoint.format(playlist_id=id)
                
                save_checks.append(self.get(endpoint, params = {
                    "ids": self.user.userprofile.spotify_username
                }))

        return self.get(endpoint, params=data)

    def get_top_items(self, data):
        type = data.pop("type")

        return self.get(ENDPOINTS["top_items"].format(type=type), params=data)

    def get_recent_tracks(self, data):
        return self.get(ENDPOINTS["saved_tracks"], params=data)
    
    def get_search_results(self, data):
        return self.get(ENDPOINTS["search"], params=data)

    def get_related_artists(self, data):
        artist_id = data.pop("artist_id")

        return self.get(ENDPOINTS['related_artists'].format(artist_id=artist_id), params=data)

    def get_recommendations(self, data):
        top_tracks = self.get_top_items({
            "type": "tracks",
            "limit": 5,
            "time_range": "short_term"
        }).json()["items"]

        ids = list(map(lambda track: track["id"], top_tracks))
        ids = ",".join(ids)

        data["seed_tracks"] = ids

        return self.get(ENDPOINTS["recommendations"], params=data)
    
    def get_saved(self, data):
        type = data.get("type", "")

        data["type"] = type[:-1]

        return self.get(ENDPOINTS[f"saved_{ type }"], params=data)

    def get_new_releases(self, data):
        return self.get(ENDPOINTS['new_releases'], params = data)

    def get_profile(self):
        return self.get(ENDPOINTS["profile"])

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

    def get(self, endpoint, params = {}):
        response = requests.get(endpoint, params = params, headers = self.get_headers())

        if response.status_code == 401:
            authorized = self.async_refresh_token()

            if authorized:
                response = requests.get(endpoint, params = params, headers=self.get_headers())
            else:
                response = {
                    'error': 'unauthorized',
                    'error_message': 'User is unauthorized'
                }

        return response

    def put(self, endpoint, data = {}, params = {}):
        data = json.dumps(data)

        response = requests.put(endpoint, params = params, data = data, headers = self.get_headers())

        if response.status_code == 401:
            authorized = self.async_refresh_token()

            if authorized:
                response = requests.put(endpoint, params = data, headers = self.get_headers())
            else:
                response = {
                    "error": "unauthorized",
                    "error_message": "User is unauthorized"
                }

        return response

    def post(self, endpoint, data = {}):
        data = json.dumps(data)

        response = requests.post(endpoint, data = data, headers = self.get_headers())

        if response.status_code == 401:
            authorized = self.async_refresh_token()

            if authorized:
                response = requests.post(endpoint, data = data, headers = self.get_headers())
            else:
                response = {
                    'error': 'unauthorized',
                    'error_message': 'User is unauthorized'
                }

        return response

    def delete(self, endpoint, params = {}):
        data = json.dumps(params)

        response = requests.delete(endpoint, params = params, headers = self.get_headers())

        if response.status_code == 401:
            authorized = self.async_refresh_token()

            if authorized:
                response = requests.delete(endpoint, params = params, headers = self.get_headers())
            else:
                response = {
                    'error': 'unauthorized',
                    'error_message': 'User is unauthorized'
                }

        return response
