from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api.spotify_client import SpotifyClient

class SaveViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request, format = None, *args, **kwargs):
        type = kwargs.get("type")
        save = request.data.get("save")
        ids = request.data.get("ids")

        rec = SpotifyClient(request.user).save({
            "type": type,
            "save": save,
            "ids": ids
        })

        rec = rec.status_code == 200
        
        return Response(rec)