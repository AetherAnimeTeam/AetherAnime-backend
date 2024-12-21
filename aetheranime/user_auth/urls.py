from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ProtectedView, UserRegistrationView, VerifyEmailView, user_status

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user/<int:user_id>/status-summary/", user_status, name="user_status"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("protected/", ProtectedView.as_view(), name="protected-view"),
]
