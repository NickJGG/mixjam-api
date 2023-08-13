from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from api.models import User
from api.serializers import UserSerializer

class CreateUserView(CreateAPIView):
    model = User
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer
