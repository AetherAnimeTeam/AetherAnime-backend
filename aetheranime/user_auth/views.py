from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .utils import generate_verification_code, send_verification_email
from .serializers import UserTokenObtainPairSerializer, UserRegistrationSerializer, UserUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.decorators import api_view
from user_auth.models import Status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

User = get_user_model()


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'access': {'type': 'string', 'example': 'eyJhbGci...'},
                    'refresh': {'type': 'string', 'example': 'eyJhbGci...'},
                    'expires_in': {'type': 'integer', 'example': 6*60*60},
                },
            },
            400: {'description': 'Invalid credentials or bad request'},
        },
    )
    def post(self, request, *args, **kwargs):
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
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(description="User registered successfully. Verification code sent to email."),
            400: OpenApiResponse(description="Bad Request"),
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            verification_code = generate_verification_code()
            print(verification_code, f"verification_code_{user.email.strip()}")
            cache.set(
                f"verification_code_{user.email.strip()}",
                verification_code,
                timeout=3600,
            )
            send_verification_email(user.email.strip(), verification_code)
            return Response(
                {"message": "User registered successfully. Verification code sent to email."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get("email").strip()
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


class UserTokenRefreshView(TokenRefreshView):
    serializer_class = UserTokenObtainPairSerializer

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'access': {'type': 'string', 'example': 'eyJhbGci...'},
                    'refresh': {'type': 'string', 'example': 'eyJhbGci...'},
                    'expires_in': {'type': 'integer', 'example': 6*60*60},
                },
            },
            400: {'description': 'Invalid credentials or bad request'},
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.user.id
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

    def put(self, request):
        try:
            user_id = request.user.id
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
