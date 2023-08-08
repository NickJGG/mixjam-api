from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class AlbumsViewset(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, album_id):
        client = SpotifyClient(request.user)

        album = client.get_album({
            "album_id": album_id
        }).json()

        album["tracks"] = album["tracks"]["items"]

        album["tracks"] = helpers.add_saved_status_to_collection(client, album["tracks"], "track")
        album = helpers.add_saved_status_to_collection(client, [album], "album")[0]
        album["tracks"] = helpers.add_artists_to_collection(client, album["tracks"])
        
        album_without_tracks = album.copy()
        album_without_tracks.pop("tracks")

        album["tracks"] = map(lambda track: {
            **track,
            "album": album_without_tracks
        }, album["tracks"])
        
        return Response(album)
