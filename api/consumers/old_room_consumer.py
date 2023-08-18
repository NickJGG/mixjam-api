import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

from api import util, spotify, serializers
from api.models import *


playback_skips = ['volume', 'get_devices', 'select_device', 'select_volume']


class OldRoomConsumer(AsyncWebsocketConsumer):

#region CONNECTION FUNCTIONS

    async def connect(self):
        room_code = self.scope['url_route']['kwargs']['room_code']
        user = self.get_user()
        room = Room.objects.get(code = room_code)

        self.room_name = room_code
        self.group_name = 'room_%s' % self.room_name
        self.user_name = user.username
        self.listening = False

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.online()
        await self.accept()

        await self.connection({
            'connection_state': {
                'connection_type': 'join',
                'user': serializers.UserSerializer(user).data
            }
        })

        await self.playlist({
            'action': 'get_state'
        })
        await self.playback({
            'action': 'get_devices'
        })
        await spotify.update_play(user, room)

    async def disconnect(self, close_code):
        await self.offline()

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

#endregion

#region RECEIVE/SEND FUNCTIONS

    async def receive(self, text_data):
        data = json.loads(text_data)

        request_type = data['type']

        data = data['data']

        if request_type == 'connection':
            await self.connection()
        elif request_type == 'playback':
            await self.playback(data)
        elif request_type == 'playlist':
            await self.playlist(data)
        elif request_type == 'admin':
            await self.admin()
    
    async def group_send(self, data):
        data['type'] = 'group_' + data['type']

        await self.channel_layer.group_send(
            self.group_name, data
        )

    async def self_send(self, type, response_data):
        await self.send(text_data=json.dumps({
            'type': type,
            'response_data': response_data
        }))
    
    async def connection(self, data):
        response_data = {
            'type': 'connection',
            'data': {**data, **{
                    
                }
            }
        }

        await self.group_send(response_data)

    async def playback(self, data):
        response_data = {
            'type': 'playback',
            'data': {**data, **{
                    
                }
            }
        }

        user = self.get_user()
        room = self.get_room()

        action = data['action']

        if action in playback_skips:
            if action in playback_skips:
                if action == 'get_devices':
                    devices = (await spotify.get_devices(user)).json()['devices']

                    response_data['data']['devices'] = devices

                    await self.self_send('devices', response_data['data'])
                elif action == 'select_device':
                    device_id = data['device_id']

                    response = spotify.select_device(user, device_id)

                    try:
                        if response.status_code == 204:
                            await spotify.update_play(user, room)
                        
                        await self.playback({
                            'action': 'get_devices'
                        })
                    except:
                        pass
                elif action == 'select_volume':
                    percentage = data['percentage']

                    response = await spotify.set_volume(user, percentage)

                    # try:
                    #     if response.status_code == 204:
                    #         await spotify.update_play(user, room)
                        
                    #     await self.playback({
                    #         'action': 'select_volume'
                    #     })
                    # except:
                    #     pass

            return

        return_data = spotify.update_playback(user, data, room=room)

        if action == 'song_end' and not return_data:
            return
        
        response_data['data']['playback'] = spotify.get_room_playback(user, room)

        await self.group_send(response_data)

    async def playlist(self, data):
        response_data = {
            'type': 'playlist',
            'data': {**data, **{
                    
                }
            }
        }

        user = self.get_user()
        room = self.get_room()

        action = data['action']

        if action == 'get_state':
            response_data['data']['playlist'] = await spotify.get_playlist_data(user, room.playlist_id)
            response_data['data']['playback'] = spotify.get_room_playback(user, room)

            if room.playlist.song_index >= len(response_data['data']['playlist']['tracks']['items']):
                room.playlist.restart()

            await self.self_send('playlist', response_data['data'])

            return
        else:
            pass

        response_data['data']['playlist'] = await spotify.get_playlist_data(user, room, listening = self.listening)

        await self.group_send(response_data)

    async def admin(self, data):
        pass

#region GROUP FUNCTIONS

    async def group_playback(self, data):
        response_data = data['data']

        user = self.get_user()
        room = self.get_room()

        action = response_data['action']

        if 'progress_ms' not in response_data:
            response_data['progress_ms'] = room.playlist.get_progress(user)

        await spotify.play_action(user, 'playlist:' + room.playlist_id, response_data, sync_play = True)

        await self.self_send('playback', response_data)

    async def group_playlist(self, data):
        response_data = data['data']

        user = self.get_user()
        room = self.get_room()

        await self.self_send('playlist', response_data)

    async def group_admin(self, data):
        response_data = None

        await self.self_send('admin', response_data)

    async def group_connection(self, request_data):
        user = self.get_user()

        if request_data['data']['connection_state']['connection_type'] == 'kick':
            self_kicked = request_data['data']['connection_state']['user']['username'] == user.username

            request_data['data']['connection_state']['self_kicked'] = self_kicked

        await self.self_send('connection', request_data)

    async def group_history_entry(self, request_action, subject, action, object = None, before_subject = None, before_object = None):
        block_data = {
            'subject': subject,
            'action': action,
            'object': object,
            'before_subject': before_subject,
            'before_object': before_object
        }

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'request_history',
                'data': {
                    'request_action': request_action,
                    # 'block': render_to_string('core/blocks/room/history-entry.html', block_data)
                }
            }
        )

    async def group_self_history_entry(self, request_action, subject, action, object = None, before_subject = None, before_object = None):
        block_data = {
            'subject': subject,
            'action': action,
            'object': object,
            'before_subject': before_subject,
            'before_object': before_object
        }

        await self.self_send('request_history', {
            'data': {
                'request_action': request_action,
                # 'block': render_to_string('core/blocks/room/history-entry.html', block_data)
            }
        })

#endregion

#region HELPER FUNCTIONS

    @database_sync_to_async
    def online(self):
        room = self.get_room()

        if room:
            room.active_users.add(self.get_user())

    @database_sync_to_async
    def offline(self):
        room = self.get_room()

        if room:
            room.active_users.remove(self.get_user())
            room.save()

            if not room.is_active():
                if room.playlist.playing:
                    room.playlist.progress_ms = util.get_adjusted_progress(room)
                    room.playlist.playing = False
                    room.playlist.save()

    def get_room(self):
        room = Room.objects.filter(code=self.room_name)

        return room[0] if room.exists() else None
    
    def print_request(self, request_data):
        print('\n=== RECEIVED REQUEST ===============')
        print('Time: ' + datetime.now().strftime('%I:%M:%S %m/%d'))
        print('User: ' + self.get_user().username)
        print('\nType: ' + request_data['type'])
        print('Data: ' + json.dumps(request_data['data'], indent = 4))
        print('==================== END REQUEST ===\n')
    
    async def get_devices(self):
        return None
    
    def get_user(self):
        return User.objects.get(username = self.scope['user'])
