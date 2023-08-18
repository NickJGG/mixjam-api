from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class TopArtistsViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        limit = int(request.query_params.get("limit", 6))

        client = SpotifyClient(request.user)

        artists = client.get_top_items({
            "type": "artists",
            "limit": limit,
            "time_range": "short_term"
        }).json()
        print(artists)
        artists = artists["items"]

        artists = helpers.add_saved_status_to_collection(client, artists, "artist")
        
        return Response(artists)