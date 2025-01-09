from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from animes.models import Anime
from user_auth.models import CustomUser, Status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class UserRegistrationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")
        self.valid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

    def test_user_registration_missing_fields(self):
        invalid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            # Пароль отсутствует
        }
        response = self.client.post(self.register_url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class VerifyEmailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.verify_url = reverse("verify_email")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            is_verified=False,
        )

    def test_email_verification_success(self):
        from django.core.cache import cache

        cache.set(
            f"verification_code_{self.user.email}",
            "123456",
            timeout=3600,
        )

        response = self.client.post(
            self.verify_url,
            data={
                "email": self.user.email,
                "code": "123456",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Email verified successfully.")
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_email_verification_invalid_code(self):
        response = self.client.post(
            self.verify_url,
            data={
                "email": self.user.email,
                "code": "wrong_code",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class ProtectedViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.protected_url = reverse("protected-view")

    def test_protected_view_with_authentication(self):
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "This is a protected resource")

    def test_protected_view_without_authentication(self):
        self.client.credentials()
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserStatusTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="password123",
        )

        self.anime = Anime.objects.create(
            title="Test Anime", description="Test Description"
        )

        Status.objects.create(user=self.user, status="active", anime_id=self.anime.id)
        Status.objects.create(user=self.user, status="inactive", anime_id=self.anime.id)

        self.status_url = reverse("user_status", kwargs={"user_id": self.user.id})
