from django.urls import path
from .views import ListAnimeView, SearchAnimeView, AnimeDetailView

urlpatterns = [
    path("", ListAnimeView.as_view(), name="list_anime"),
    path("search/", SearchAnimeView.as_view(), name="search_anime"),
    path(
        "<int:anime_id>/",
        AnimeDetailView.as_view(),
        name="get_anime_detail",
    ),
]
