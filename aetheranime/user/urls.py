from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AnimeRatingView,
    DeactivateAccountView,
    GetAnimeStatusView,
    SetAnimeStatusView,
    UserRegistrationView,
    VerifyEmailView,
    UserProfileView,
    UserTokenObtainPairView,
    SendVerificationCode, UserStatusView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("token/", UserTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("", UserProfileView.as_view(), name="user_profile"),
    path("<int:user_id>", UserProfileView.as_view(), name="user_profile"),
    path("send-code/", SendVerificationCode.as_view(), name="send_code"),
    path("deactivate/", DeactivateAccountView.as_view(), name="deactivate_account"),
    # path(
    #     "<int:user_id>/anime/<int:anime_id>/set-status/",
    #     SetAnimeStatusView.as_view(),
    #     name="set_anime_status",
    # ),
    path("status/<int:anime_id>", UserStatusView.as_view(), name="user_status"),
    path("anime/<int:anime_id>/rating/", AnimeRatingView.as_view(), name="anime_rating"),
    path(
        "user/<int:user_id>/anime/<int:anime_id>/status/",
        GetAnimeStatusView.as_view(),
        name="get_anime_status",
    ),
]
