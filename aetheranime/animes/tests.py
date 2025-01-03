from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Anime, Genre, AnimePreview
from user_auth.models import CustomUser, Status
from .serializers import AnimePreviewSerializer  # импортируем сериализатор


class AnimeAppTests(APITestCase):
    def setUp(self):
        self.user_1 = CustomUser.objects.create_user(
            username="testuser1", password="password", email="testuser1@example.com"
        )
        self.user_2 = CustomUser.objects.create_user(
            username="testuser2", password="password", email="testuser2@example.com"
        )

        self.genre = Genre.objects.create(id=1, name="Action")
        self.anime = Anime.objects.create(
            name_ru="Test Anime",
            name_original="Test Original",
            description="Test Description",
            poster_url="http://example.com/poster.jpg",
            score=8.5,
            score_count=100,
            age_rating="PG-13",
            studios="Test Studio",
            duration=24,
            episodes=12,
            episodes_aired=12,
            release_date="2023-01-01",
            aired_date="2023-12-31",
            status="released",
        )
        self.anime.genres.add(self.genre)

        self.anime_preview = AnimePreview.objects.create(
            anime_id=self.anime.id,
            name_ru="Test Anime Preview",
            poster_url="http://example.com/preview.jpg",
            score=7.8,
            status="released",
        )

        Status.objects.create(user=self.user_1, anime_id=self.anime.id, status="active")
        Status.objects.create(
            user=self.user_2, anime_id=self.anime.id, status="inactive"
        )

    # def test_popular_anime(self):
    #     url = reverse("search_anime") + "?status=latest"
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_search_anime(self):
    #     url = reverse("search_anime") + "?name=Test"
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anime_status_summary(self):
        url = reverse("anime_status_summary", kwargs={"anime_id": self.anime.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"active": 1, "inactive": 1})
