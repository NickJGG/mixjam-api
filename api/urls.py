from django.urls import path
from django.urls.conf import include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("user", views.UserViewSet, "user")
router.register("friends", views.FriendsViewSet, "friends")

urlpatterns = [
    path("", include(router.urls)),
    path("connect/", views.ConnectSpotify.as_view()),

    path("recommendations/<str:type>/", views.RecommendationsViewSet.as_view()),
    path("releases/", views.NewReleasesViewSet.as_view()),
    path("top/tracks/", views.TopTracksViewSet.as_view()),
    path("top/artists/", views.TopArtistsViewSet.as_view()),
    path("recent/tracks/", views.RecentTracksViewSet.as_view()),
    path("saved/", views.SavedViewSet.as_view()),

    path("search/", views.SearchViewSet.as_view()),
    path("save/<str:type>/", views.SaveViewSet.as_view()),

    path("notifications/<int:notification_id>/", views.NotificationsViewSet.as_view()),
]