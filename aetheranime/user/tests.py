from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Status
from django.core.cache import cache

User = get_user_model()


class UserRegistrationViewTests(APITestCase):
    def test_user_registration_success(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "date_of_birth": "2000-01-01",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_user_registration_invalid_data(self):
        url = reverse("register")
        data = {
            "username": "",
            "email": "invalid-email",
            "password": "short",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserTokenObtainPairViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_verified=True,
        )

    def test_token_obtain_success(self):
        url = reverse("token_obtain_pair")
        data = {
            "email": "test@example.com",
            "password": "testpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_obtain_invalid_credentials(self):
        url = reverse("token_obtain_pair")
        data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VerifyEmailViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_verified=False,
        )
        self.verification_code = "123456"
        cache.set(
            f"verification_code_test@example.com", self.verification_code, timeout=3600
        )

    def test_verify_email_success(self):
        url = reverse("verify_email")
        data = {
            "email": "test@example.com",
            "code": self.verification_code,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_verify_email_invalid_code(self):
        url = reverse("verify_email")
        data = {
            "email": "test@example.com",
            "code": "wrongcode",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_verified=True,
        )
        self.client.force_authenticate(user=self.user)
        Status.objects.create(user=self.user, anime_id=1, status="watching")
        Status.objects.create(user=self.user, anime_id=2, status="completed")

    def test_get_user_profile_success(self):
        url = reverse("user_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["status_summary"]["watching"], 1)
        self.assertEqual(response.data["status_summary"]["completed"], 1)

    def test_update_user_profile_success(self):
        url = reverse("user_profile")
        data = {
            "username": "updateduser",
            "email": "updated@example.com",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updated@example.com")


class SendVerificationCodeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_verified=False,
        )

    def test_send_verification_code_success(self):
        url = reverse("send_code")
        data = {
            "email": "test@example.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cache.get(f"verification_code_test@example.com"))

    def test_send_verification_code_invalid_email(self):
        url = reverse("send_code")
        data = {
            "email": "nonexistent@example.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
