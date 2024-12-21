import asyncio

from asgiref.sync import sync_to_async
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.http import JsonResponse

from .models import Anime, Genre, AnimePreview
from .serializers import AnimeSerializer, GenreSerializer, AnimePreviewSerializer
from utils.anime_meta_parser import get_animes_by_name, get_details
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user_auth.models import Status


@api_view(["GET"])
def root(request):
    return Response({"status": "Active"})


@api_view(["GET"])
def search_anime(request):
    name = request.GET.get("name", "")
    order = request.GET.get("order", "popularity")
    status = request.GET.get("status", "")
    limit = int(request.GET.get("limit", 10))
    page = int(request.GET.get("page", 1))

    data = get_animes_by_name(name, status=status, order=order, limit=limit, page=page)
    return Response(data)


@api_view(["GET"])
def popular_anime(request):
    previews = AnimePreview.objects.all()
    serializer = AnimePreviewSerializer(previews, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def detailed_meta(request, anime_id):
    try:
        anime_object = Anime.objects.get(pk=anime_id)
    except Anime.DoesNotExist:
        return Response(
            {"error": "Anime with this ID does not exist"},
            status=404,
        )

    serializer = AnimeSerializer(anime_object)
    return Response(serializer.data)


@api_view(["GET"])
def search_magnet(request, name):
    return Response({"list": []})


class AnimePreviewListView(ListAPIView):
    queryset = AnimePreview.objects.all()
    serializer_class = AnimePreviewSerializer


class AnimeDetailView(RetrieveAPIView):
    queryset = Anime.objects.all()
    serializer_class = AnimeSerializer

    def get_object(self):
        anime_id = self.kwargs.get("anime_id")
        return Anime.objects.get(pk=anime_id)


class GenreListView(ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


@api_view(["GET"])
def anime_status_summary(request, anime_id):
    statuses = (
        Status.objects.filter(anime_id=anime_id)
        .values("status")
        .annotate(count=Count("status"))
    )
    data = {status["status"]: status["count"] for status in statuses}
    return Response(data)
