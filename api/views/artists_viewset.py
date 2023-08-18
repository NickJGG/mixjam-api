from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class ArtistsViewset(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, artist_id):
        client = SpotifyClient(request.user)

        artist = client.get_artist({
            "artist_id": artist_id
        }).json()

        artist = helpers.add_saved_status_to_collection(client, [artist], "artist")[0]
        # artist = helpers.add_artists_to_collection(client, artist)
        
        return Response(artist)
