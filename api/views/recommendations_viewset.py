from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers, SpotifyClient

SEED_LIMIT = 5

class RecommendationsViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, type, format = None, *args, **kwargs):
        limit = int(request.query_params.get("limit", 6))

        client = SpotifyClient(request.user)
        tracks = client.get_recommendations({
            "limit": limit
        }).json()["tracks"]

        tracks = helpers.add_saved_status_to_collection(client, tracks, "track")
        tracks = helpers.add_artists_to_collection(client, tracks)

        # if type == 'tracks':
        #     track_ids = []

        #     for track in rec['items']:
        #         track_ids.append(track['id'])

        #     rec = spotify.get_recommendations(request.user, type, track_ids, limit = limit)
        #     rec = rec.json()
        # elif type == 'artists':
        #     artist_ids = []

        #     for track in rec['items']:
        #         artist_ids.append(track['artists'][0]['id'])

        #     rec_artists = []

        #     for artist_id in artist_ids:
        #         rec = spotify.get_artists_similar(request.user, artist_id).json()

        #         for artist in rec['artists']:
        #             if artist not in rec_artists:
        #                 rec_artists.append(artist)

        #                 break
            
        #     rec = {
        #         'artists': rec_artists
        #     }

        return Response(tracks)
