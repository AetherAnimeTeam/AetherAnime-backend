from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .utils import generate_verification_code, send_verification_email
from .serializers import (
    AnimeRatingSerializer,
    StatusSerializer,
    UserTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Count
from .models import AnimeRating, CustomUser, Status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

User = get_user_model()


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "example": "eyJhbGci..."},
                    "refresh": {"type": "string", "example": "eyJhbGci..."},
                    "expires_in": {"type": "integer", "example": 6 * 60 * 60},
                },
            },
            400: {"description": "Invalid credentials or bad request"},
        },
    )
    def post(self, request, *args, **kwargs):
        user = User.objects.get(email=request.data.get("email"))
        if not user.is_verified:
            return Response(
                status=status.HTTP_403_FORBIDDEN, data={"detail": "Not verified"}
            )
        if not user.is_active:
            return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "Not active"})
        return super().post(request, *args, **kwargs)


class UserRegistrationView(APIView):
    """
    Handles user registration.

    Response:
    - Success: HTTP 201 Created
    - Failure: HTTP 400 Bad Request
    """

    @extend_schema(
        request=UserRegistrationSerializer,
        examples=[
            OpenApiExample(
                "Credentials",
                value={
                    "username": "",
                    "email": "",
                    "password": "",
                    "date_of_birth": "",
                    "profile_picture": "",
                },
                request_only=True,
            )
        ],
        responses={
            201: OpenApiResponse(
                description="User registered successfully. Verification code sent to email."
            ),
            400: OpenApiResponse(description="Bad Request"),
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            verification_code = generate_verification_code()

            cache.set(
                f"verification_code_{user.email.strip()}",
                verification_code,
                timeout=3600,
            )
            send_verification_email(user.email.strip(), verification_code)
            return Response(
                {
                    "message": "User registered successfully. Verification code sent to email."
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationCode(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = email.strip()
        if not User.objects.filter(email=email).exists():
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        verification_code = generate_verification_code()

        send_verification_email(email, verification_code)
        cache.set(
            f"verification_code_{email}",
            verification_code,
            timeout=3600,
        )

        return Response(
            {"message": "Verification code sent to email."}, status=status.HTTP_200_OK
        )


class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"error": "Email and code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = email.strip()

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


class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, anime_id):
        user_status = get_object_or_404(Status, user=request.user, anime_id=anime_id)
        return Response(StatusSerializer(user_status).data, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, user_id=None):
        try:
            if not user_id:
                user_id = request.user.id

            user = User.objects.get(id=user_id)
            if not user.is_active:
                return Response(
                    {"error": "Аккаунт деактивирован."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user = User.objects.get(id=user_id)
            statuses = (
                Status.objects.filter(user_id=user_id)
                .values("status")
                .annotate(count=Count("status"))
            )
            status_data = {status["status"]: status["count"] for status in statuses}

            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_picture": (
                    user.profile_picture.url if user.profile_picture else None
                ),
                "tag": user.tag,
                "status_summary": status_data,
            }
            return Response(user_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request):
        try:
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            serializer = UserUpdateSerializer(user, data=request.data)
            if serializer.is_valid():
                updated_user = serializer.save()
                return Response(
                    {
                        "message": "User updated successfully.",
                        "user": UserUpdateSerializer(updated_user).data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class DeactivateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.deactivate()  # Деактивируем аккаунт
        return Response(
            {"message": "Аккаунт успешно деактивирован."},
            status=status.HTTP_200_OK,
        )


class SetAnimeStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id, anime_id):
        # Проверяем, что пользователь изменяет свой собственный статус
        if request.user.id != user_id:
            return Response(
                {"error": "Вы не можете изменять статус другого пользователя."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = get_object_or_404(CustomUser, id=user_id)
        new_status = request.data.get("status")

        if new_status not in dict(Status.STATUS_CHOICES).keys():
            return Response(
                {"error": f"Недопустимый статус. Допустимые значения: {list(Status.STATUS_CHOICES)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Получаем текущий статус аниме для пользователя
        try:
            status_obj = Status.objects.get(user=user, anime_id=anime_id)
            if status_obj.status != new_status:
                status_obj.status = new_status
                status_obj.save()
                message = "Статус успешно обновлён."
            else:
                message = "Статус не изменился."
        except Status.DoesNotExist:
            status_obj = Status.objects.create(user=user, anime_id=anime_id, status=new_status)
            message = "Статус успешно создан."

        serializer = StatusSerializer(status_obj)
        return Response({"message": message, "data": serializer.data}, status=status.HTTP_200_OK)


class GetAnimeStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, anime_id):
        # Проверяем, что пользователь запрашивает свой собственный статус
        if request.user.id != user_id:
            return Response(
                {"error": "Вы не можете запрашивать статус другого пользователя."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Получаем пользователя и статус аниме
        user = get_object_or_404(CustomUser, id=user_id)
        try:
            status_obj = Status.objects.get(user=user, anime_id=anime_id)
            serializer = StatusSerializer(status_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Status.DoesNotExist:
            # Если статус не найден, возвращаем ответ с пустым статусом
            return Response(
                {"anime_id": anime_id, "status": None},
                status=status.HTTP_200_OK,
            )


class AnimeRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, anime_id):
        """
        Получает оценку аниме для текущего пользователя.
        """
        try:
            rating = AnimeRating.objects.get(user=request.user, anime_id=anime_id)
            serializer = AnimeRatingSerializer(rating)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AnimeRating.DoesNotExist:
            return Response(
                {"anime_id": anime_id, "score": None},
                status=status.HTTP_200_OK,
            )

    def post(self, request, anime_id):
        """
        Создает или обновляет оценку аниме для текущего пользователя.
        Если оценка уже существует, она обновляется. Если нет — создается.
        """
        user = request.user
        score = request.data.get("score")

        if not score:
            return Response(
                {"error": "Поле 'score' обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Используем get_or_create для поиска или создания оценки
        rating, created = AnimeRating.objects.get_or_create(
            user=user,
            anime_id=anime_id,
            defaults={"score": score},  # Значение по умолчанию, если оценка создается
        )

        if not created:
            # Если оценка уже существует, обновляем её
            rating.score = score
            rating.save()

        serializer = AnimeRatingSerializer(rating)
        return Response(
            {
                "message": "Оценка создана." if created else "Оценка обновлена.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
