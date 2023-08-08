from .user_consumer import UserConsumer
from .party_consumer import PartyConsumer

from .old_user_consumer import OldUserConsumer
from .old_room_consumer import OldRoomConsumer

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_to_channel(channel_name, message):
    async_to_sync(get_channel_layer().group_send)(channel_name, {
        "type": "response",
        "data": message
    })

def send_to_user(username, message):
    send_to_channel(f"user_{ username }", message)