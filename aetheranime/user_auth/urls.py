from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    VerifyEmailView,
    TokenRefreshView,
    UserProfileView,
    user_status,
    CustomTokenObtainPairView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("user/<int:user_id>/status-summary/", user_status, name="user_status"),
    path("user/<int:user_id>/", UserProfileView.as_view(), name="user_profile"),
]
