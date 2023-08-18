from django.urls import path

from .consumers import UserConsumer, PartyConsumer, OldRoomConsumer

websocket_urlpatterns = [
    path('ws/u/<str:username>', UserConsumer.as_asgi()),
    path('ws/p/<str:party_code>', PartyConsumer.as_asgi()),
    path('ws/r/<str:room_code>', OldRoomConsumer.as_asgi()),
]
