import os
import base64
import json
import requests
import time
import math

from channels.db import database_sync_to_async

import requests_async

from django.utils import timezone
from django.template.loader import render_to_string

from .models import *
from . import util

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

endpoints = {
    'refresh': 'https://accounts.spotify.com/api/token',

    'player': 'https://api.spotify.com/v1/me/player/',
    'play': 'https://api.spotify.com/v1/me/player/play',
    'pause': 'https://api.spotify.com/v1/me/player/pause',
    'seek': 'https://api.spotify.com/v1/me/player/seek',
    'previous': 'https://api.spotify.com/v1/me/player/previous',
    'next': 'https://api.spotify.com/v1/me/player/next',
    'devices': 'https://api.spotify.com/v1/me/player/devices',
    'volume': 'https://api.spotify.com/v1/me/player/volume',
    'shuffle': 'https://api.spotify.com/v1/me/player/shuffle',
    'repeat': 'https://api.spotify.com/v1/me/player/repeat',
    'song': 'https://api.spotify.com/v1/me/player/currently-playing',
    'recently_played': 'https://api.spotify.com/v1/me/player/recently-played',

    'profile': 'https://api.spotify.com/v1/me/',
    'current_user_playlists': 'https://api.spotify.com/v1/me/playlists',
    'top_items': 'https://api.spotify.com/v1/me/top/',
    'top_tracks': 'https://api.spotify.com/v1/me/top/tracks/',

    'playlist': 'https://api.spotify.com/v1/playlists/',
    'artists': 'https://api.spotify.com/v1/artists/',

    'recommendations': 'https://api.spotify.com/v1/recommendations/',
    'new_releases': 'https://api.spotify.com/v1/browse/new-releases',
}

player_actions = ['play', 'play_direct', 'pause']

enable_play = True

# region Room Player

def update_playback(user, data, room=None):
    return_data = None

    action = data['action']

    if action == 'play':
        room.playlist.playing = True
    elif action == 'pause':
        room.playlist.playing = False

        room.playlist.progress_ms = util.get_adjusted_progress(room)
    elif action == 'play_direct' or action == 'previous' or action == 'next':
        print(room)

        room.playlist.progress_ms = 0
        room.playlist.playing = True
        
        if action == 'previous':
            room.playlist.previous_song()
        elif action == 'next':
            room.playlist.next_song()
        else:
            room.playlist.song_index = data['offset']
            room.playlist.progress_ms = 0
    elif action == 'seek':
        print(data['progress_ms'])

        room.playlist.progress_ms = data['progress_ms']
    elif action == 'song_end':
        return_data = room.playlist.song_end()
    
    room.playlist.last_action = timezone.now()
    room.playlist.save()

    print_update(room)

    return return_data

def print_update(room):
    print('""""" PLAYLIST UPDATE """""')
    print('PLAYING: ' + str(room.playlist.playing))
    print('SONG INDEX: ' + str(room.playlist.song_index))
    print('PROGRESS(MS): ' + str(room.playlist.progress_ms))
    print('LAST ACTION: ' + str(room.playlist.last_action))
    print('"""""""""""""""""""""""""""')

async def update_play(user, room):
    if enable_play:
        response = await play(user, 'playlist:' + room.playlist_id, offset = room.playlist.song_index)
        response = await sync(user, progress_ms = room.playlist.get_progress(user))

        await set_repeat(user)
        await set_shuffle(user)

        if not room.playlist.playing:
            return await pause(user)
        
        if response is not None:
            try:
                code = response.status_code

                if code == 404:
                    return 404
            except:
                pass
        
        return response
    else:
        return None

async def action(user, data):
    await play_action(user, '', data)
async def play_action(user, context, data, sync_play = False):
    response = None

    action = data['action']
    progress_ms = data['progress_ms'] if 'progress_ms' in data else 0

    if enable_play:
        if action in ['play', 'play_direct', 'play_specific', 'play_artist']:
            if sync_play:
                response = await sync(user, progress_ms = progress_ms)
        
            if action == 'play_specific':
                response = await play_specific(user, data['track_uri'] if 'track_uri' in data else None)
            elif action == 'play_artist':
                response = await play(user, data['artist_uri'] if 'artist_uri' in data else None)
            else:
                response = await play(user, context, offset = data['offset'] if 'offset' in data else None) 
        else:
            if action == 'pause':
                response = await pause(user)
            elif action == 'seek':
                response = await seek(user, progress_ms = progress_ms)
            elif action == 'previous':
                response = await previous(user)
            elif action == 'next':
                response = await next(user)
            
            if sync_play:
                response = await sync(user, progress_ms = progress_ms)

    return response

async def get_profile(user):
    return await async_get(user, endpoints['profile'])

async def get_devices(user):
    return await async_get(user, endpoints['devices'])

def get_playlist(user, code):
    return get(user, endpoints['playlist'] + code)
def get_playlists(user):
    return get(user, endpoints['current_user_playlists'])

def get_top_items(user, type = 'tracks', time_range = 'short_term', limit = 5):
    return get(user, endpoints['top_items'] + type, params = {
        'time_range': time_range,
        'limit': limit
    })

def get_related_artists(user, artist_id):
    return get(user, endpoints['artists'] + artist_id + '/related-artists')

def get_new_releases(user, limit = 20):
    return get(user, endpoints['new_releases'], params = {
        'limit': limit
    })

def get_top_tracks(user, limit = 20):
    return get(user, endpoints['top_tracks'], params = {
        'limit': limit
    })

def get_recently_played(user, limit = 5):
    return get(user, endpoints['recently_played'], params = {
        'limit': limit
    })

def get_recommendations(user, seed_label, seed, limit = 20):
    return get(user, endpoints['recommendations'], params = {
        'seed_' + seed_label: seed,
        'limit': limit
    })

@database_sync_to_async
def set_user_picture(user, url):
    user.profile.picture = url
    user.profile.save()

def select_device(user, device_id):
    return put(user, endpoints['player'], data = {
        'device_ids': [device_id],
        'play': True
    })

async def set_volume(user, volume_percent):
    return await async_put(user, endpoints['volume'], params = {
        'volume_percent': volume_percent
    })

async def play(user, context, offset = None):
    data = {}

    if context is not None and context != '':
        if context.split(':')[0] != 'spotify':
            context = f'spotify:{context}'

        data['context_uri'] = context

    if offset is not None:
        data['offset'] = {
            'position': offset
        }

    return await async_put(user, endpoints['play'], data = data)
async def play_specific(user, track_uri):
    data = {
        'uris': [track_uri]
    }

    return await async_put(user, endpoints['play'], data = data)

async def pause(user):
    return await async_put(user, endpoints['pause'])

async def sync(user, progress_ms = 0):
    #seek_ms = progress_ms if progress_ms is not None else room.playlist.get_progress(user)

    return await seek(user, progress_ms = progress_ms)

async def seek(user, progress_ms):
    params = {
        'position_ms': progress_ms
    }

    return await async_put(user, endpoints['seek'], params = params)

async def previous(user):
    return await async_post(user, endpoints['previous'])

async def next(user):
    return await async_post(user, endpoints['next'])

async def set_shuffle(user):
    params = {
        'state': False
    }

    return await async_put(user, endpoints['shuffle'], params = params)

async def set_repeat(user):
    params = {
        'state': 'context'
    }

    return await async_put(user, endpoints['repeat'], params = params)

# endregion

# region Get States

def get_playlist_data_na(user, playlist_id):
    playlist_data = get(user, endpoints['playlist'] + playlist_id).json()

    if playlist_data['tracks']['total'] > 100:
        for x in range(math.floor(playlist_data['tracks']['total'] / 100)):
            tracks = get(user, endpoints['playlist'] + playlist_id + '/tracks', params = {
                'offset': (x + 1) * 100
            }).json()

            playlist_data['tracks']['items'].extend(tracks['items'])

    return playlist_data

async def get_playlist_data(user, playlist_id):
    playlist_data = await async_get(user, endpoints['playlist'] + playlist_id)
    playlist_data = playlist_data.json()

    if playlist_data['tracks']['total'] > 100:
        for x in range(math.floor(playlist_data['tracks']['total'] / 100)):
            tracks = (await async_get(user, endpoints['playlist'] + playlist_id + '/tracks', params = {
                'offset': (x + 1) * 100
            })).json()

            playlist_data['tracks']['items'].extend(tracks['items'])

    return playlist_data

def get_room_playback(user, room):
    playback_data = {
        'is_playing': room.playlist.playing,
        'progress_ms': room.playlist.get_progress(user),
        'song_index': room.playlist.song_index,
    }

    return playback_data

async def get_playback(user):
   return await async_get(user, endpoints['player'])

# async def get_playlist_state(user, room_code):
#     room = Room.objects.filter(code = room_code)

#     if not room.exists() or room[0].playlist_id is None:
#         return None

#     room = room[0]

#     playlist_data = await get_playlist_data(user, room.playlist_id)

#     if room.playlist_image_url is None:
#         await util.update_playlist_image(room, playlist_data['images'][0]['url'])

#     return playlist_data

# endregion

# region Authorization

def get_headers(user):
    return {
        "Authorization": f"Bearer {user.profile.access_token}"
    }

def get_token_headers():
    client_creds_b64 = get_client_credentials()

    return {
        "Authorization": f"Basic {client_creds_b64}"
    }

def get_client_credentials():
    if not client_secret or not client_id:
        raise Exception("You must set client_id and client_secret")

    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())

    return client_creds_b64.decode()

async def async_refresh_token(user):
    response = await requests_async.post(endpoints['refresh'], data = {
        'grant_type': 'refresh_token',
        'refresh_token': user.profile.refresh_token
    }, headers = get_token_headers())

    r_json = response.json()

    if response.status_code < 400:
        user.profile.access_token = r_json['access_token']
        user.profile.authorized = True
    else:
        user.profile.authorized = False
    
    user.profile.save()

    return user.profile.authorized

def refresh_token(user):
    response = requests.post(endpoints['refresh'], data = {
        'grant_type': 'refresh_token',
        'refresh_token': user.profile.refresh_token
    }, headers = get_token_headers())

    r_json = response.json()

    if response.status_code < 400:
        user.profile.access_token = r_json['access_token']
        user.profile.authorized = True
    else:
        user.profile.authorized = False
    
    user.profile.save()

    return user.profile.authorized

# endregion

# region Requests

async def async_get(user, endpoint, params = {}):
    response = await requests_async.get(endpoint, params = params, headers = get_headers(user))

    if response.status_code == 401:
        authorized = await async_refresh_token(user)

        if authorized:
            response = await requests_async.get(endpoint, params = params, headers=get_headers(user))
        else:
            response = {
                'error': 'unauthorized',
                'error_message': 'User is unauthorized'
            }

    return response

def get(user, endpoint, params = {}):
    response = requests.get(endpoint, params = params, headers = get_headers(user))

    if response.status_code == 401:
        authorized = refresh_token(user)

        if authorized:
            response = requests.get(endpoint, params = params, headers=get_headers(user))
        else:
            response = {
                'error': 'unauthorized',
                'error_message': 'User is unauthorized'
            }

    return response

async def async_put(user, endpoint, data = {}, params = {}):
    data = json.dumps(data)

    print(data)

    response = await requests_async.put(endpoint, params = params, data = data, headers = get_headers(user))

    if response.status_code == 401:
        authorized = await async_refresh_token(user)

        if authorized:
            response = await requests_async.put(endpoint, params = data, headers = get_headers(user))
        else:
            response = {
                'error': 'unauthorized',
                'error_message': 'User is unauthorized'
            }

    return response

def put(user, endpoint, data = {}, params = {}):
    data = json.dumps(data)

    response = requests.put(endpoint, params = params, data = data, headers = get_headers(user))

    if response.status_code == 401:
        authorized = refresh_token(user)

        if authorized:
            response = requests.put(endpoint, params = data, headers = get_headers(user))
        else:
            response = {
                'error': 'unauthorized',
                'error_message': 'User is unauthorized'
            }

    return response

async def async_post(user, endpoint, data = {}):
    data = json.dumps(data)

    response = await requests_async.post(endpoint, data = data, headers = get_headers(user))

    if response.status_code == 401:
        authorized = await async_refresh_token(user)

        if authorized:
            response = await requests_async.post(endpoint, data = data, headers = get_headers(user))
        else:
            response = {
                'error': 'unauthorized',
                'error_message': 'User is unauthorized'
            }

    return response

def post(user, endpoint, data = {}):
    data = json.dumps(data)

    response = requests.post(endpoint, data = data, headers = get_headers(user))

    if response.status_code == 401:
        authorized = refresh_token(user)

        if authorized:
            response = requests.post(endpoint, data = data, headers = get_headers(user))
        else:
            response = {
                'error': 'unauthorized',
                'error_message': 'User is unauthorized'
            }

    return response

# endregion