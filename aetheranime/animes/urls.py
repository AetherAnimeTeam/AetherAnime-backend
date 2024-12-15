from django.urls import path
from . import views

urlpatterns = [
    path("", views.root, name="root"),
    path("search/", views.search_anime, name="search_anime"),
    path("popular/", views.popular_anime, name="popular_anime"),
    path("detailed/<int:anime_id>/", views.detailed_meta, name="detailed_meta"),
    path("magnet/<str:name>/", views.search_magnet, name="search_magnet"),
    path("previews/", views.AnimePreviewListView.as_view(), name="anime_previews"),
    path("anime/<int:anime_id>/", views.AnimeDetailView.as_view(), name="anime_detail"),
    path("genres/", views.GenreListView.as_view(), name="genres_list"),
]
