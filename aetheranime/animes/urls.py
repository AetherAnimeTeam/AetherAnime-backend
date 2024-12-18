from django.urls import path
from . import views

urlpatterns = [
    path("", views.root, name="root"),
    path("search/", views.search_anime, name="search_anime"),
    path("magnet/<str:name>/", views.search_magnet, name="search_magnet"),
    path("anime/<int:anime_id>/", views.AnimeDetailView.as_view(), name="anime_detail"),
    path("anime/<int:anime_id>/status-summary/", views.anime_status_summary, name="anime_status_summary"),
]
