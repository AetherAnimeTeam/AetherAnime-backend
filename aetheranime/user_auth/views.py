from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.cache import cache
from .utils import (
    generate_verification_code,
    send_verification_email,
)
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.decorators import api_view
from user_auth.models import CustomUser, Status


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            verification_code = generate_verification_code()
            cache.set(
                f"verification_code_{user.email}",
                verification_code,
                timeout=3600,
            )
            send_verification_email(user.email, verification_code)
            return Response(
                {
                    "message": "User registered successfully. Verification code sent to email."
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"error": "Email and code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cached_code = cache.get(f"verification_code_{email}")
        if cached_code == code:
            try:
                user = CustomUser.objects.get(email=email)
                user.is_verified = True
                user.save()
                cache.delete(f"verification_code_{email}")
                return Response(
                    {"message": "Email verified successfully."},
                    status=status.HTTP_200_OK,
                )
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            {"error": "Invalid verification code."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected resource"})


@api_view(["GET"])
def user_status(request, user_id):
    statuses = (
        Status.objects.filter(user_id=user_id)
        .values("status")
        .annotate(count=Count("status"))
    )
    data = {status["status"]: status["count"] for status in statuses}
    return Response(data)
