from django.urls import path
from .views import ListAnimeView, SearchAnimeView, AnimeDetailView, SetStatusView

urlpatterns = [
    path(
        "<str:order>/<str:status>/<int:page>/<int:limit>",
        ListAnimeView.as_view(),
        name="list_anime",
    ),
    path("search/<str:name>", SearchAnimeView.as_view(), name="search_anime"),
    path(
        "<int:anime_id>/",
        AnimeDetailView.as_view(),
        name="get_anime_detail",
    ),
    path("status/<int:anime_id>/", SetStatusView.as_view(), name="set_status"),
]
