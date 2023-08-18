from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.helpers import get_notifications
from api.models import User
from api.serializers import UserSerializer

class UserViewSet(APIView):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, username):
        user = User.objects.filter(username=username)
        
        if not user.exists():
            return Response({ "success": False })
    
        user = UserSerializer(user[0]).data

        return Response({
            "user": user
        })
