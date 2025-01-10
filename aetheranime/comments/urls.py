from django.urls import path
from .views import (
    CommentAPIView,
    # ReplyAPIView,
)

urlpatterns = [
    path("<int:anime_id>/", CommentAPIView.as_view(), name="comments",),
    path("<int:anime_id>/<int:comment_id>/", CommentAPIView.as_view(), name="replies", ),

]
