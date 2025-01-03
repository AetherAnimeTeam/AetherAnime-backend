from django.urls import path
from .views import (
    GetCommentsAPIView,
    AddWatchedHistoryAPIView,
    SetStatusAPIView,
    RemoveStatusAPIView,
)

urlpatterns = [
    path("<int:anime_id>/", GetCommentsAPIView.as_view(), name="get_comments"),
    path(
        "<int:anime_id>/<int:comment_id>/",
        GetCommentsAPIView.as_view(),
        name="get_replies",
    ),
    path("history/", AddWatchedHistoryAPIView.as_view(), name="add_watched"),
]
