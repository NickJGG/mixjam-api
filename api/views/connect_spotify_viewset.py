import os
import base64
import requests

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from api.spotify_client import SpotifyClient

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

class ConnectSpotify(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request, format = None):
        if 'code' in request.data:
            code = request.data['code']

            base_url = os.environ.get("SPOTIFY_REDIRECT_URL")
            redirect_uri = f"{base_url}/callback/"

            print(redirect_uri)

            token_data = {
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }

            client_creds = f"{client_id}:{client_secret}"
            client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

            print(os.environ)

            token_headers = {"Authorization": f"Basic {client_creds_b64}"}

            response = requests.post('https://accounts.spotify.com/api/token', data = token_data, headers = token_headers)

            try:
                access_token = response['access_token']
                refresh_token = response['refresh_token']

                request.user.profile.access_token = access_token
                request.user.profile.refresh_token = refresh_token
                request.user.profile.save()

                profile = SpotifyClient(request.user).get_profile()
                request.user.profile.spotify_username = profile.json()["display_name"]
                request.user.profile.authorized = True
                request.user.profile.save()

                return Response({
                    'success': True
                })
            except Exception as e:
                request.user.profile.authorized = False
                
                print(e)
        else:
            pass

        return Response({
            'success': False
        })
