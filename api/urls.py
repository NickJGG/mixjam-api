from django.urls import path
from django.urls.conf import include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('user', views.UserViewSet, 'user')
router.register('room', views.RoomViewSet, 'room')

urlpatterns = [
    path('', include(router.urls)),
    path('connect/', views.ConnectSpotify.as_view()),

    path('room/playlist/<str:room_code>/', views.RoomPlaylistViewSet.as_view()),
    path('playlist/<str:playlist_code>/', views.PlaylistViewSet.as_view()),
    path('playlists/', views.PlaylistsViewSet.as_view()),

    path('recommendations/<str:type>/', views.RecommendationsViewSet.as_view()),
    
    path('releases/', views.NewReleasesViewSet.as_view()),
    path('top/tracks/', views.TopTracksViewSet.as_view()),
]