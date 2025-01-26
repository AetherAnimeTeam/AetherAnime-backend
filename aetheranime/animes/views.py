from typing import Optional

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.anime_meta_parser import get_animes_by_name
from utils.anime_meta_parser import get_details

from .serializers import AnimeSerializer, AnimePreviewSerializer
from user.models import Status


class ListAnimeView(APIView):
    """
    Возвращает список аниме по параметрам (сортировка, статус, пагинация).
    """

    serializer_class = AnimePreviewSerializer

    def get(
        self,
        request,
        order: str = "popularity",
        status: str = "latest",
        page: int = 1,
        limit: int = 10,
        name: Optional[str] = None,
    ):

        animes = get_animes_by_name(order=order, status=status, page=page, limit=limit)
        serializer = self.serializer_class(animes, many=True)

        return Response(serializer.data)


class SetStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, anime_id: int):
        # try:
        print(request.data)
        s = Status.objects.get_or_create(anime_id=anime_id, user=request.user, defaults={"status": request.data["status"]})

        if not s[1]:
            s[0].status = request.data["status"]
            s[0].save()
        # except Exception as e:
        #     print(e)
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


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
