from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class PlaylistsViewset(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, playlist_id):
        client = SpotifyClient(request.user)

        playlist = client.get_playlist({
            "playlist_id": playlist_id
        })

        playlist["tracks"] = list(map(lambda item: item["track"], playlist["tracks"]["items"]))

        # playlist["tracks"] = helpers.add_saved_status_to_collection(client, playlist["tracks"], "track")
        # playlist = helpers.add_saved_status_to_collection(client, [playlist], "playlist")[0]
        playlist["tracks"] = helpers.add_artists_to_collection(client, playlist["tracks"])
        
        playlist_without_tracks = playlist.copy()
        playlist_without_tracks.pop("tracks")

        playlist["tracks"] = map(lambda track: {
            **track,
            "playlist": playlist_without_tracks
        }, playlist["tracks"])
        
        return Response(playlist)
