import os
import requests
import base64

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from . import spotify

from .models import *
from .serializers import *
from . import spotify

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return User.objects.filter(id = self.request.user.id)

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        user = self.request.user

        return Room.objects.filter(users = user)

class RoomPlaylistViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        room_code = kwargs.get('room_code')
        room = Room.objects.filter(code = room_code)

        if room.exists():
            return Response(spotify.get_playlist_data_na(request.user, room[0].playlist_id))
    
        return Response({ 'success': False, 'message': 'Room not found' })

class PlaylistViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        playlist_id = kwargs.get('playlist_code')

        playlist_data = spotify.get_playlist_data_na(request.user, playlist_id)
        
        return Response(playlist_data)

class NewReleasesViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        limit = 12

        rec = spotify.get_new_releases(request.user, limit=limit)
        rec = rec.json()
        
        return Response(rec)

class TopTracksViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        limit = 12

        rec = spotify.get_top_tracks(request.user, limit=limit)
        rec = rec.json()
        
        return Response(rec)

class PlaylistsViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format = None, *args, **kwargs):
        playlists = spotify.get_playlists(request.user)
    
        return Response(playlists.json())

class RecommendationsViewSet(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, type, format = None, *args, **kwargs):
        limit = 12

        rec = spotify.get_top_items(request.user, time_range = 'short_term', limit = limit)

        try:
            rec = rec.json()
            
            if type == 'tracks':
                track_ids = []

                for track in rec['items']:
                    track_ids.append(track['id'])

                rec = spotify.get_recommendations(request.user, type, track_ids, limit = limit)
                rec = rec.json()
            elif type == 'artists':
                artist_ids = []

                for track in rec['items']:
                    artist_ids.append(track['artists'][0]['id'])

                rec_artists = []

                for artist_id in artist_ids:
                    rec = spotify.get_related_artists(request.user, artist_id).json()

                    for artist in rec['artists']:
                        if artist not in rec_artists:
                            rec_artists.append(artist)

                            break
                
                rec = {
                    'artists': rec_artists
                }

            return Response(rec)
        except:
            return Response({
                'success': False,
                'message': 'Something went wrong'
            })

class ConnectSpotify(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request, format = None):
        if 'code' in request.data:
            code = request.data['code']

            redirect_uri = 'http://localhost:3000/callback/' if os.environ.get('DJANGO_DEVELOPMENT') else 'https://mixjam.io/callback/'

            token_data = {
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }

            client_creds = f"{client_id}:{client_secret}"
            client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

            token_headers = {"Authorization": f"Basic {client_creds_b64}"}

            r = requests.post('https://accounts.spotify.com/api/token', data = token_data, headers = token_headers)

            try:
                data = r.json()

                access_token = data['access_token']
                refresh_token = data['refresh_token']

                request.user.userprofile.access_token = access_token
                request.user.userprofile.refresh_token = refresh_token
                request.user.userprofile.save()

                return Response({
                    'success': True
                })
            except:
                print('\n\nDIDNOTWORK\n\n')
        else:
            pass

        return Response({
            'success': False
        })