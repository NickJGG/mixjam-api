from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class ArtistsAlbumsViewset(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, artist_id):
        client = SpotifyClient(request.user)

        albums = client.get_artists_albums({
            "artist_id": artist_id
        })

        albums = list(filter(lambda album: album["album_type"] != "single", albums))

        albums = helpers.add_saved_status_to_collection(client, albums, "artist")
        albums = helpers.add_artists_to_collection(client, albums)
        
        return Response(albums)
