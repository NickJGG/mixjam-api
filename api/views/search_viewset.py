from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api import helpers
from api.spotify_client import SpotifyClient

class SearchViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        limit = int(request.query_params.get("limit", 6))
        query = request.query_params.get("query")
        type = request.query_params.get("type", "track,artist,playlist,album")

        client = SpotifyClient(request.user)

        rec = client.get_search_results({
            "q": query,
            "limit": limit,
            "type": type
        })
        rec = rec.json()

        if "errors" not in rec:
            for key, val in rec.items():
                rec[key] = val["items"]

            for type in type.split(","):
                type_plural = type + "s"
                
                if type_plural in ["artists", "playlists"]:
                    continue

                collection = rec[type_plural]
                rec[type_plural] = helpers.add_saved_status_to_collection(client, collection, type)
                rec[type_plural] = helpers.add_artists_to_collection(client, collection)
        
        return Response(rec)
