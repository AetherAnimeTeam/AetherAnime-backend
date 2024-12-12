from django.urls import path
from .views import GetCommentsAPIView, AddWatchedHistoryAPIView, SetStatusAPIView, RemoveStatusAPIView

urlpatterns = [
    path('comments/<int:anime_id>/', GetCommentsAPIView.as_view(), name='get_comments'),
    path('comments/<int:anime_id>/<int:comment_id>/', GetCommentsAPIView.as_view(), name='get_replies'),
    path('history/', AddWatchedHistoryAPIView.as_view(), name='add_watched'),
    path('status/', SetStatusAPIView.as_view(), name='set_status'),
    path('status/<int:anime_id>/', RemoveStatusAPIView.as_view(), name='remove_status'),
]
