from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import PartyInvite
from api.serializers import PartySerializer

class NotificationsViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request, notification_id, *args, **kwargs):
        notification = PartyInvite.objects.get(id=notification_id)
        action = request.data.get("action")

        response_data = notification.perform_action(action)

        if response_data["success"]:
            response_data["party"] = PartySerializer(notification.party).data

        return Response(response_data)