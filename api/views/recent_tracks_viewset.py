from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class RecentTracksViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        limit = int(request.query_params.get("limit", 6))

        client = SpotifyClient(request.user)

        tracks = client.get_recent_tracks({
            "limit": limit
        }).json()["items"]

        tracks = list(map(lambda item: item["track"], tracks))
        ids = list(map(lambda track: track["id"], tracks))
        tracks = helpers.add_saved_status_to_collection(client, tracks, ids, "track")

        return Response(tracks)