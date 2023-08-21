from django.utils.crypto import get_random_string

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api.spotify_client import SpotifyClient
from api.consumers import send_to_user
from api.models import Party, PartyInvite, FriendRequest, User, Notification
from api.models.notification import NotificationType
from api.serializers import PartySerializer, PartyInviteSerializer, FriendSerializer, FriendRequestSerializer

class NotificationsViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_invite(self, notification):
        invite = PartyInvite.objects.filter(notification__id=notification.id)

        if invite.exists():
            return invite[0]
        
        return FriendRequest.objects.filter(notification__id=notification.id)[0]

    def put(self, request, notification_id):
        notification = Notification.objects.get(id=notification_id)
        action = self.request.query_params.get("action")

        invite = self.get_invite(notification)

        response_data = invite.perform_action(action)

        if response_data["success"]:
            type = invite.get_type()

            if type == NotificationType.PARTY_INVITE:
                response_data["join_party"] = True
                response_data["party"] = PartySerializer(invite.party).data
            elif type == NotificationType.FRIEND_REQUEST:
                response_data["friend"] = FriendSerializer(notification.sender).data

                send_to_user(notification.sender, {
                    "type": "friend",
                    "notification": FriendSerializer(notification.receiver).data
                })

        return Response(response_data)

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("userId")
        party_code = request.data.get("partyCode")
        type = NotificationType.MATCH[request.data.get("type")]

        sender = self.request.user
        receiver = User.objects.get(id=user_id)

        response_data = {
            "success": False
        }

        if sender.profile.party is None:
            while True:
                new_code = get_random_string(length=6)

                parties = Party.objects.filter(code=new_code)

                if not parties.exists():
                    break

            new_party = Party.objects.create(code=new_code, creator=self.request.user)
            new_party.allowed_users.add(self.request.user)
            new_party.save()
            new_party.join(sender)

            spotify_client = SpotifyClient(sender)
            current_state = spotify_client.get_state({})

            track = current_state.get("item", "")

            if track != "":
                track_uri = track.get("uri", "")
                context = current_state.get("context", "")
                context_uri = context.get("uri", "")

                if track_uri != "" and context_uri != "":
                    new_party.play_track({
                        "track_uri": track_uri,
                        "context_uri": context_uri,
                    })

            response_data["join_party"] = True
            response_data["party"] = PartySerializer(new_party).data
            response_data["success"] = True

        if sender.profile.party.can_invite(sender, receiver):
            notification = Notification(
                sender=sender,
                receiver=receiver
            )
            notification.save()

            if type == NotificationType.PARTY_INVITE:
                party_invite = PartyInvite(
                    notification=notification,
                    party=sender.profile.party
                )
                party_invite.save()

                send_to_user(receiver.username, {
                    "type": "notification",
                    "notification": PartyInviteSerializer(party_invite).data
                })
            elif type == NotificationType.FRIEND_REQUEST:
                friend_request = FriendRequest(
                    notification=notification
                )
                friend_request.save()

                send_to_user(receiver.username, {
                    "type": "friend",
                    "notification": FriendRequestSerializer(friend_request).data
                })

            response_data["success"] = True
        
        print(response_data)

        return Response(response_data)
