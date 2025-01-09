from django.urls import path
from .views import (
    UserRegistrationView,
    VerifyEmailView,
    UserProfileView,
    UserTokenObtainPairView, UserTokenRefreshView, SendVerificationCode,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("token/", UserTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token_refresh"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("", UserProfileView.as_view(), name="user_profile"),
    path("send-code/", SendVerificationCode.as_view(), name="send_code"),
]
