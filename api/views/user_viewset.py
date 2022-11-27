from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import User, PartyInvite
from api.serializers import UserSerializer, PartyInviteSerializer

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = User.objects.filter(id = self.request.user.id)
        
        if queryset.exists():
            queryset[0].notifications = self.get_notifications()

        return queryset
    
    def list(self, request, *args, **kwargs):
        serialized_user = UserSerializer(request.user).data
        serialized_user["notifications"] = self.get_notifications()

        print(serialized_user)

        return Response(serialized_user)
    
    def get_notifications(self):
        party_invites = PartyInvite.objects.filter(notification__receiver=self.request.user)
        serialized_invites = PartyInviteSerializer(party_invites, many=True).data

        return serialized_invites
