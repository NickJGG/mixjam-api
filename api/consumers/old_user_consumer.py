import json

from channels.generic.websocket import AsyncWebsocketConsumer

from api import spotify
from api.models import *

class OldUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.get_user()

        self.room_name = user.username
        self.group_name = 'user_%s' % self.room_name

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        user.userprofile.go_online()

        await self.playback({
            'action': 'get_devices'
        })

        if user.userprofile.online_count == 1:
            for friend in user.userprofile.friends.all():
                active_room = Room.objects.filter(users = friend, active_users = friend)

                if active_room.exists():
                    active_room = active_room[0]
                else:
                    active_room = None

                await self.channel_layer.group_send(
                    'user_%s' % friend.username,
                    {
                        'type': 'request_connection',
                        'data': {
                            'connection_state': {
                                'connection_type': 'online',
                                'user': {
                                    'username': user
                                },
                                # 'friend_block': render_to_string('core/blocks/side-panel-items/friend.html', {
                                #     'friend': user,
                                #     'user': friend,
                                #     'room': active_room
                                # })
                            }
                        }
                    }
                )

    # DISCONNECT FUNCTION
    async def disconnect(self, close_code):
        user = self.get_user()

        user.userprofile.go_offline()

        if user.userprofile.online_count == 0:
            for friend in user.userprofile.friends.all():
                active_room = Room.objects.filter(users = friend, active_users = friend)

                if active_room.exists():
                    active_room = active_room[0]
                else:
                    active_room = None

                await self.channel_layer.group_send(
                    'user_%s' % friend.username,
                    {
                        'type': 'request_connection',
                        'data': {
                            'connection_state': {
                                'connection_type': 'offline',
                                'user': {
                                    'username': user.username
                                },
                                # 'friend_block': render_to_string('core/blocks/side-panel-items/friend.html', {
                                #     'friend': user,
                                #     'user': friend,
                                #     'room': active_room
                                # })
                            }
                        }
                    }
                )

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

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
    
    async def playback(self, data):
        response_data = {
            'type': 'playback',
            'data': {**data, **{
                    
                }
            }
        }

        user = self.get_user()

        action = data['action']

        if action == 'get_devices':
            devices = (await spotify.get_devices(user)).json()['devices']

            response_data['data']['devices'] = devices

            await self.self_send('devices', response_data['data'])

            return
        elif action == 'select_device':
            device_id = data['device_id']

            response = spotify.select_device(user, device_id)
            
            await self.playback({
                'action': 'get_devices'
            })
        elif action == 'select_volume':
            percentage = data['percentage']

            response = await spotify.set_volume(user, percentage)
        elif action == 'get_profile':
            profile = await spotify.get_profile(user)
            profile = profile.json()
        elif action != 'get_state':
            await spotify.play_action(user, '', data)

        state = await spotify.get_playback(user)

        try:
            state = state.json()
        except:
            state = {}

        await self.self_send('playback', {
            'playback': state
        })
    
    async def connection(self, data):
        response_data = {
            'type': 'connection',
            'data': {**data, **{
                    
                }
            }
        }

        user = self.get_user()

        action = data['action']

    async def playlist(self, data):
        response_data = {
            'type': 'playlist',
            'data': {**data, **{
                    
                }
            }
        }

        user = self.get_user()

        action = data['action']

    async def admin(self, data):
        response_data = {
            'type': 'admin',
            'data': {**data, **{
                    
                }
            }
        }

        user = self.get_user()

        action = data['action']
    
    def get_user(self):
        return User.objects.get(username = self.scope['user'])
