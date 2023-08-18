from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.helpers import get_notifications
from api.models import User
from api.serializers import UserSerializer

class SelfViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = UserSerializer(self.request.user).data
        user["notifications"] = get_notifications(self.request.user)

        return Response({
            "user": user
        })
