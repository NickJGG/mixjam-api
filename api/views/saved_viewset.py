from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from api import helpers

from api.spotify_client import SpotifyClient

class SavedViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        limit = int(request.query_params.get("limit", 6))
        type = request.query_params.get("type")

        client = SpotifyClient(request.user)

        rec = client.get_saved({
            "type": type,
            "limit": limit
        })

        if type in rec:
            rec = rec[type]

        if "items" in rec:
            rec = rec["items"]

        if isinstance(rec, list) and len(rec) > 0 and type[:-1] in rec[0]:
            rec = list(map(lambda item: item[type[:-1]], rec))
        
        if type not in ["artists", "playlists"]:
            rec = helpers.add_artists_to_collection(client, rec)

        rec = helpers.add_saved_status_to_collection(client, rec, type[:-1])

        return Response(rec)
