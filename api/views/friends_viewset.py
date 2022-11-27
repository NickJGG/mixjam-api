from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from api.models import User
from api.serializers import UserSerializer

class FriendsViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        user = User.objects.filter(id = self.request.user.id)

        if user.exists():
            return user.first().userprofile.friends

        return None