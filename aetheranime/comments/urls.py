from django.urls import path
from .views import (
    GetCommentsAPIView,
    AddCommentAPIView,
    AddReplyAPIView,
    DeleteCommentAPIView,
)

urlpatterns = [
    path("<int:anime_id>/", GetCommentsAPIView.as_view(), name="get_comments"),
    path(
        "<int:anime_id>/<int:comment_id>/",
        GetCommentsAPIView.as_view(),
        name="get_replies",
    ),
    path(
        "<int:anime_id>/", AddCommentAPIView.as_view(), name="add_comment"
    ),  # для создания комментария
    path(
        "<int:anime_id>/<int:comment_id>/", AddReplyAPIView.as_view(), name="add_reply"
    ),  # для создания ответа
    path(
        "<int:comment_id>/", DeleteCommentAPIView.as_view(), name="delete_comment"
    ),  # для удаления комментария
]
