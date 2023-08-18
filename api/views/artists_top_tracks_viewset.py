from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class ArtistsTopTracksViewset(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, artist_id):
        client = SpotifyClient(request.user)

        tracks = client.get_artists_top_tracks({
            "artist_id": artist_id
        }).json()["tracks"]

        tracks = helpers.add_saved_status_to_collection(client, tracks, "artist")
        tracks = helpers.add_artists_to_collection(client, tracks)
        
        return Response(tracks)
