from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class ArtistsSimilarViewset(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, artist_id):
        client = SpotifyClient(request.user)

        artists = client.get_artists_similar({
            "artist_id": artist_id
        })

        artists = helpers.add_saved_status_to_collection(client, artists, "artist")
        
        return Response(artists)
