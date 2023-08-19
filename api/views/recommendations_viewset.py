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
        })

        tracks = helpers.add_saved_status_to_collection(client, tracks, "track")
        tracks = helpers.add_artists_to_collection(client, tracks)

        return Response(tracks)
