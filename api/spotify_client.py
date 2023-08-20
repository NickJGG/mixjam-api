import os
import base64
import json
import requests_async
import requests

import math
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
    "add_queue": "https://api.spotify.com/v1/me/player/queue",

    "profile": "https://api.spotify.com/v1/me/",
    "current_user_playlists": "https://api.spotify.com/v1/me/playlists",
    "top_items": "https://api.spotify.com/v1/me/top/{type}",

    "playlist": "https://api.spotify.com/v1/playlists/{playlist_id}",
    "playlist_tracks": "https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
    
    "album": "https://api.spotify.com/v1/albums/{album_id}",

    "artist": "https://api.spotify.com/v1/artists/{artist_id}",
    "artists": "https://api.spotify.com/v1/artists",
    "artists_similar": "https://api.spotify.com/v1/artists/{artist_id}/related-artists",
    "artists_top_tracks": "https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
    "artists_albums": "https://api.spotify.com/v1/artists/{artist_id}/albums",

    "recommendations": "https://api.spotify.com/v1/recommendations/",
    "new_releases": "https://api.spotify.com/v1/browse/new-releases",
    "search": "https://api.spotify.com/v1/search",

    "saved_tracks": "https://api.spotify.com/v1/me/tracks",
    "saved_artists": "https://api.spotify.com/v1/me/following/",
    "saved_albums": "https://api.spotify.com/v1/me/albums",
    "saved_playlists": "https://api.spotify.com/v1/me/playlists",

    "track_is_saved": "https://api.spotify.com/v1/me/tracks/contains/",
    "artist_is_saved": "https://api.spotify.com/v1/me/following/contains/",
    "album_is_saved": "https://api.spotify.com/v1/me/albums/contains/",
    "playlist_is_saved": "https://api.spotify.com/v1/playlists/{playlist_id}/followers/contains/",
    "tracks_save": "https://api.spotify.com/v1/me/tracks",
    "albums_save": "https://api.spotify.com/v1/me/albums",
}

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

class RecommendationLength:
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"

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
        context_uri = data.get("context_uri", "")
        track_uri = data.get("track_uri")

        if context_uri is not None and context_uri is not "":
            put_data = {}
            
            put_data["context_uri"] = context_uri

            if track_uri is not None and track_uri is not "":
                put_data["offset"] = {
                    "uri": track_uri
                }

            return await self.async_put(ENDPOINTS["play"], data=put_data)

        post_params = {
            "uri": data["track_uri"]
        }

        await self.async_post(ENDPOINTS["add_queue"], params=post_params)

        return await self.next({})

    async def play_context(self, data):
        put_data = {}

        context_uri = data.get("context_uri", None)
        track_index = data.get("track_index", -1)

        if context_uri is not None:
            put_data["context_uri"] = context_uri

        if track_index > -1:
            put_data["offset"] = track_index
        
        return await self.async_put(ENDPOINTS["play"], data=put_data)

    async def previous(self, data):
        return await self.async_post(ENDPOINTS['previous'])
    
    async def next(self, data):
        return await self.async_post(ENDPOINTS['next'])

    def seek(self, data):
        put_params = {
            "position_ms": data["progress_ms"]
        }

        return self.put(ENDPOINTS['seek'], params=put_params)

    async def async_seek(self, data):
        put_params = {
            "position_ms": data["progress_ms"]
        }

        return await self.async_put(ENDPOINTS['seek'], params=put_params)

    async def add_queue(self, data):
        post_params = {
            "uri": data["track_uri"]
        }

        return await self.async_post(ENDPOINTS["add_queue"], params=post_params)

    async def track_end(self, data):
        return await self.get_state_async(data)

    def get_state(self, data):
        time.sleep(.25)
        return self.get(ENDPOINTS["player"])
    
    async def get_state_async(self, data):
        time.sleep(.5)
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
                    "ids": self.user.profile.spotify_username
                }))

        return self.get(endpoint, params=data)

    def get_playlist(self, data):
        playlist_id = data.pop("playlist_id")

        playlist = self.get(ENDPOINTS["playlist"].format(playlist_id=playlist_id), params=data)

        if playlist['tracks']['total'] > 99:
            for x in range(math.floor(playlist['tracks']['total'] / 100)):
                data["offset"] = (x + 1) * 100

                response = self.get(ENDPOINTS["playlist_tracks"].format(playlist_id=playlist_id), params=data)

                playlist['tracks']['items'].extend(response['items'])

        return playlist

    def get_album(self, data):
        album_id = data.pop("album_id")

        return self.get(ENDPOINTS["album"].format(album_id=album_id), params=data)
    
    def get_artist(self, data):
        artist_id = data.pop("artist_id")

        return self.get(ENDPOINTS["artist"].format(artist_id=artist_id), params=data)

    def get_artists_similar(self, data):
        artist_id = data.pop("artist_id")

        return self.get(ENDPOINTS["artists_similar"].format(artist_id=artist_id), params=data).get("artists", [])
    
    def get_artists_top_tracks(self, data):
        artist_id = data.pop("artist_id")
        data["market"] = "US"

        return self.get(ENDPOINTS["artists_top_tracks"].format(artist_id=artist_id), params=data).get("tracks", [])
    
    def get_artists_albums(self, data):
        artist_id = data.pop("artist_id")

        return self.get(ENDPOINTS["artists_albums"].format(artist_id=artist_id), params=data).get("items", [])

    def get_top_items(self, data):
        type = data.pop("type")

        return self.get(ENDPOINTS["top_items"].format(type=type), params=data).get("items", [])

    def get_recent_tracks(self, data):
        return self.get(ENDPOINTS["saved_tracks"], params=data).get("items", [])
    
    def get_search_results(self, data):
        return self.get(ENDPOINTS["search"], params=data)

    def get_artists(self, data):
        ids = data.pop("ids")[:50]
        
        data["ids"] = ",".join(ids)

        return self.get(ENDPOINTS['artists'], params=data)

    def get_recommendations(self, data):
        max_tracks = 5
        # num_short_term_tracks = math.floor(max_tracks / 2)
        num_short_term_tracks = 2
        num_medium_term_tracks = max_tracks - num_short_term_tracks

        short_term_tracks = self.get_top_items({
            "type": "tracks",
            "limit": num_short_term_tracks,
            "time_range": "short_term"
        })

        medium_term_tracks = self.get_top_items({
            "type": "tracks",
            "limit": num_medium_term_tracks,
            "time_range": "medium_term"
        })

        ids = list(map(lambda track: track["id"], short_term_tracks + medium_term_tracks))
        ids = ",".join(ids)

        data["seed_tracks"] = ids

        return self.get(ENDPOINTS["recommendations"], params=data).get("tracks", [])
    
    def get_saved(self, data):
        type = data.pop("type")

        if type == "artists":
            data["type"] = type[:-1]

        return self.get(ENDPOINTS[f"saved_{ type }"].format(user_id=self.user.profile.spotify_username), params=data)

    def get_new_releases(self, data):
        return self.get(ENDPOINTS['new_releases'], params = data).get("albums", []).get("items", [])

    def get_profile(self):
        return self.get(ENDPOINTS["profile"])

    #region AUTH

    async def async_refresh_token(self):
        response = await requests_async.post(ENDPOINTS["refresh"], data = {
            "grant_type": "refresh_token",
            "refresh_token": self.user.profile.refresh_token
        }, headers = self.get_token_headers())

        r_json = response.json()

        if response.status_code < 400:
            self.user.profile.access_token = r_json["access_token"]
            self.user.profile.authorized = True
        else:
            self.user.profile.authorized = False
        
        self.user.profile.save()

        return self.user.profile.authorized

    def refresh_token(self):
        response = requests.post(ENDPOINTS["refresh"], data = {
            "grant_type": "refresh_token",
            "refresh_token": self.user.profile.refresh_token
        }, headers = self.get_token_headers())

        r_json = response.json()

        if response.status_code < 400:
            self.user.profile.access_token = r_json["access_token"]
            self.user.profile.authorized = True
        else:
            self.user.profile.authorized = False
        
        self.user.profile.save()

        return self.user.profile.authorized
    
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
            "Authorization": f"Bearer {self.user.profile.access_token}"
        }
    
    #endregion

    #region HTTP

    async def async_get(self, endpoint, params = {}):
        response = await requests_async.get(endpoint, params = params, headers = self.get_headers())

        if response.status_code == 401:
            self.refresh_token()

            response = await requests_async.get(endpoint, params = params, headers=self.get_headers())

        return response.json() if response.status_code != 204 else {}

    async def async_put(self, endpoint, data = {}, params = {}):
        data = json.dumps(data)

        response = await requests_async.put(endpoint, params = params, data = data, headers = self.get_headers())

        if response.status_code == 401:
            self.refresh_token()

            response = await requests_async.put(endpoint, params = data, headers = self.get_headers())

        return response.json() if response.status_code != 204 else {}

    async def async_post(self, endpoint, data = {}, params = {}):
        data = json.dumps(data)

        response = await requests_async.post(endpoint, data = data, params = params, headers = self.get_headers())

        if response.status_code == 401:
            self.refresh_token()

            response = await requests_async.post(endpoint, data = data, params = params, headers = self.get_headers())

        return response.json() if response.status_code != 204 else {}

    def get(self, endpoint, params = {}):
        response = requests.get(endpoint, params = params, headers = self.get_headers())

        if response.status_code == 401:
            self.refresh_token()

            response = requests.get(endpoint, params = params, headers=self.get_headers())

        return response.json() if response.status_code != 204 else {}

    def put(self, endpoint, data = {}, params = {}):
        data = json.dumps(data)

        response = requests.put(endpoint, params = params, data = data, headers = self.get_headers())

        if response.status_code == 401:
            self.refresh_token()

            response = requests.put(endpoint, params = data, headers = self.get_headers())

        return response.json() if response.status_code != 204 else {}

    def post(self, endpoint, data = {}):
        data = json.dumps(data)

        response = requests.post(endpoint, data = data, headers = self.get_headers())

        if response.status_code == 401:
            self.refresh_token()

            response = requests.post(endpoint, data = data, headers = self.get_headers())

        return response.json() if response.status_code != 204 else {}

    def delete(self, endpoint, params = {}):
        response = requests.delete(endpoint, params = params, headers = self.get_headers())

        if response.status_code == 401:
            self.refresh_token()

            response = requests.delete(endpoint, params = params, headers = self.get_headers())

        return response.json() if response.status_code != 204 else {}

    #endregion
