from typing import Optional

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.http import JsonResponse
from django.db.models import Count
from .models import Anime, AnimePreview, Genre
from .serializers import AnimeSerializer, AnimePreviewSerializer
from rest_framework.views import APIView
from utils.anime_meta_parser import get_details

from utils.anime_meta_parser import get_animes_by_name


class ListAnimeView(APIView):
    """
    Возвращает список аниме по параметрам (сортировка, статус, пагинация).
    """

    serializer_class = AnimePreviewSerializer

    def get(self, request, order: str="popularity",
            status: str="latest", page: int=1, limit: int=10, name: Optional[str] = None):

        animes = get_animes_by_name(order=order, status=status, page=page, limit=limit)
        serializer = self.serializer_class(animes, many=True)

        return Response(serializer.data)


class SearchAnimeView(APIView):
    """
    Поиск аниме по названию.
    """

    serializer_class = AnimePreviewSerializer

    def get(self, request, name: str):
        animes = get_animes_by_name(name=name, limit=10)

        serializer = self.serializer_class(animes, many=True)
        return Response(serializer.data)


class AnimeDetailView(APIView):
    """
    Получить детали аниме по ID, используя данные из внешнего источника.
    """

    serializer_class = AnimeSerializer

    def get(self, request, anime_id, *args, **kwargs):
        try:
            # Получаем данные о аниме с использованием функции из anime_meta_parser.py в папке utils
            anime = get_details(anime_id)
        except Exception as e:
            return Response({"error": f"Anime not found: {str(e)}"}, status=404)

        # Сериализация данных
        serializer = self.serializer_class(anime)
        return Response(serializer.data)
