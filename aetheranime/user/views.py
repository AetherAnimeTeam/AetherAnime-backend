from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .utils import generate_verification_code, send_verification_email
from .serializers import UserTokenObtainPairSerializer, UserRegistrationSerializer, UserUpdateSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Count
from .models import Status
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
        user = User.objects.get(email=request.data.get('email'))
        if not user.is_verified:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'Not verified'})
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


class SendVerificationCode(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email are required."}, status=status.HTTP_400_BAD_REQUEST, )

        email = email.strip()
        if not User.objects.filter(email=email).exists():
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        verification_code = generate_verification_code()

        send_verification_email(email, verification_code)
        cache.set(
            f"verification_code_{email}",
            verification_code,
            timeout=3600,
        )

        return Response({"message": "Verification code sent to email."}, status=status.HTTP_200_OK)


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


class DeactivateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.deactivate()  # Деактивируем аккаунт
        return Response(
            {"message": "Аккаунт успешно деактивирован."},
            status=status.HTTP_200_OK,
        )
