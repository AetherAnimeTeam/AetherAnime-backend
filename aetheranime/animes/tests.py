from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from .serializers import AnimePreviewSerializer


class ListAnimeViewTests(APITestCase):
    @patch("animes.views.get_animes_by_name")
    def test_list_anime_by_popularity(self, mock_get_animes_by_name):
        # Мокируем данные, возвращаемые функцией get_animes_by_name
        mock_get_animes_by_name.return_value = [
            {
                "russian": "Naruto",
                "poster": {"url": "http://example.com/poster.jpg"},
                "score": 8.5,
                "status": "released",
                "id": "1",
            },
            {
                "russian": "One Piece",
                "poster": {"url": "http://example.com/poster2.jpg"},
                "score": 7.5,
                "status": "ongoing",
                "id": "2",
            },
        ]

        url = reverse("list_anime", kwargs={"order": "popularity", "status": "latest", "page": 1, "limit": 10})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["russian"], "Naruto")
        self.assertEqual(response.data[1]["russian"], "One Piece")

    @patch("animes.views.get_animes_by_name")
    def test_list_anime_by_status(self, mock_get_animes_by_name):
        # Мокируем данные, возвращаемые функцией get_animes_by_name
        mock_get_animes_by_name.return_value = [
            {
                "russian": "Naruto",
                "poster": {"url": "http://example.com/poster.jpg"},
                "score": 8.5,
                "status": "released",
                "id": "1",
            }
        ]

        url = reverse("list_anime", kwargs={"order": "popularity", "status": "released", "page": 1, "limit": 10})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["russian"], "Naruto")


class SearchAnimeViewTests(APITestCase):
    @patch("animes.views.get_animes_by_name")
    def test_search_anime_by_name(self, mock_get_animes_by_name):
        # Мокируем данные, возвращаемые функцией get_animes_by_name
        mock_get_animes_by_name.return_value = [
            {
                "russian": "Naruto",
                "poster": {"url": "http://example.com/poster.jpg"},
                "score": 8.5,
                "status": "released",
                "id": "1",
            }
        ]

        url = reverse("search_anime", kwargs={"name": "Naruto"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["russian"], "Naruto")

    @patch("animes.views.get_animes_by_name")
    def test_search_anime_no_results(self, mock_get_animes_by_name):
        # Мокируем пустой результат
        mock_get_animes_by_name.return_value = []

        url = reverse("search_anime", kwargs={"name": "Bleach"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class AnimeDetailViewTests(APITestCase):
    @patch("animes.views.get_details")
    def test_get_anime_detail(self, mock_get_details):
        # Мокируем данные, возвращаемые функцией get_details
        mock_get_details.return_value = {
            "name_ru": "Naruto",
            "name_original": "Naruto",
            "description": "A story about a ninja.",
            "poster_url": "http://example.com/poster.jpg",
            "genres": ["Action", "Adventure"],
            "score": 8.5,
            "score_count": 1000,
            "age_rating": "PG-13",
            "studios": ["Studio Pierrot"],
            "duration": 24,
            "episodes": 220,
            "episodes_aired": 220,
            "fandubbers": ["Fandubber 1"],
            "fansubbers": ["Fansubber 1"],
            "release_date": "2002-10-03",
            "status": "released",
            "related_material": [{"type": "manga", "id": 1}],
            "trailer_url": "http://example.com/trailer.mp4",
        }

        url = reverse("get_anime_detail", kwargs={"anime_id": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name_ru"], "Naruto")
        self.assertEqual(response.data["score"], 8.5)

    @patch("animes.views.get_details")
    def test_get_anime_detail_not_found(self, mock_get_details):
        # Мокируем исключение, если аниме не найдено
        mock_get_details.side_effect = Exception("Anime not found")

        url = reverse("get_anime_detail", kwargs={"anime_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Anime not found: Anime not found")
