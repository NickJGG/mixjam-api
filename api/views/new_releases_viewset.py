from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class NewReleasesViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        limit = request.query_params.get("limit", 6)

        client = SpotifyClient(request.user)

        releases = client.get_new_releases({
            "limit": limit
        })

        releases = helpers.add_saved_status_to_collection(client, releases, "track")

        return Response(releases)
