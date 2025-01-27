from django.urls import path
from .views import (
    CommentAPIView,
    CommentDislikeAPIView,
    CommentLikeAPIView,
    UserCommentsAPIView,
)

urlpatterns = [
    path(
        "<int:anime_id>/",
        CommentAPIView.as_view(),
        name="comments",
    ),
    path(
        "<int:anime_id>/<int:comment_id>/",
        CommentAPIView.as_view(),
        name="replies",
    ),
    path(
        "<int:anime_id>/<int:comment_id>/like/",
        CommentLikeAPIView.as_view(),
        name="comment-like",
    ),
    path(
        "<int:anime_id>/<int:comment_id>/dislike/",
        CommentDislikeAPIView.as_view(),
        name="comment-dislike",
    ),
    path('user/<int:user_id>/comments/', UserCommentsAPIView.as_view(), name='user_comments'),
]
