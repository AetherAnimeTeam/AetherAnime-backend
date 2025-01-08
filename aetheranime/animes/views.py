from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.http import JsonResponse
from django.db.models import Count
from .models import Anime, AnimePreview, Genre
from .serializers import AnimeSerializer, AnimePreviewSerializer
from rest_framework.views import APIView
from utils.anime_meta_parser import get_details


class ListAnimeView(APIView):
    """
    Возвращает список аниме по параметрам (сортировка, статус, пагинация).
    """

    serializer_class = AnimePreviewSerializer

    def get(self, request, *args, **kwargs):
        order = request.GET.get("order", "popularity")
        status = request.GET.get("status", "")
        limit = int(request.GET.get("limit", 10))
        page = int(request.GET.get("page", 1))

        previews = AnimePreview.objects.all()
        if status:
            previews = previews.filter(status=status)
        if order:
            previews = previews.order_by(order)

        start = (page - 1) * limit
        end = start + limit
        serializer = self.serializer_class(previews[start:end], many=True)

        return Response(serializer.data)


class SearchAnimeView(APIView):
    """
    Поиск аниме по названию.
    """

    serializer_class = AnimePreviewSerializer

    def get(self, request, *args, **kwargs):
        name = request.GET.get("name", "")
        if not name:
            return Response(
                {"error": "Parameter 'name' is required"},
                status=400,
            )
        previews = AnimePreview.objects.filter(name_ru__icontains=name)
        serializer = self.serializer_class(previews, many=True)
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
