from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .utils import generate_verification_code, send_verification_email
from .serializers import UserRegistrationSerializer, UserUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.decorators import api_view
from user_auth.models import Status

User = get_user_model()


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
                user = User.objects.get(email=email)
                user.is_verified = True
                user.save()
                cache.delete(f"verification_code_{email}")
                return Response(
                    {"message": "Email verified successfully."},
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            {"error": "Invalid verification code."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_token = str(refresh.access_token)
            return Response({"access": new_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            statuses = (
                Status.objects.filter(user_id=user_id)
                .values("status")
                .annotate(count=Count("status"))
            )
            status_data = {status["status"]: status["count"] for status in statuses}

            # Пример с аватаром
            user_data = {
                "username": user.username,
                "email": user.email,
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
                "tag": user.tag,
                "status_summary": status_data,
            }
            return Response(user_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserUpdateSerializer(user, data=request.data)
            if serializer.is_valid():
                updated_user = serializer.save()
                return Response(
                    {"message": "User updated successfully.", "user": UserUpdateSerializer(updated_user).data},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def user_status(request, user_id):
    # Получаем все статусы для указанного пользователя
    statuses = (
        Status.objects.filter(user_id=user_id)
        .values("status")
        .annotate(count=Count("status"))
    )
    
    # Формируем сводку, где ключами будут статусы, а значениями — количество
    status_summary = {status["status"]: status["count"] for status in statuses}
    
    # Статусы по умолчанию (если для них нет записей в базе данных)
    default_statuses = [
        "watching", "completed", "on_hold", "dropped", "plan_to_watch"
    ]
    
    # Добавляем нулевые значения для статусов, которые могут быть не найдены
    for status_item in default_statuses:
        if status_item not in status_summary:
            status_summary[status_item] = 0

    return Response(status_summary)
