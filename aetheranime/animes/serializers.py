from rest_framework import serializers
from .models import Anime, Genre, AnimePreview


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class AnimePreviewSerializer(serializers.Serializer):
    russian = serializers.CharField()
    poster = serializers.DictField()
    score = serializers.FloatField()
    status = serializers.CharField()
    id = serializers.CharField()


class AnimeSerializer(serializers.Serializer):
    name_ru = serializers.CharField()
    name_original = serializers.CharField()
    description = serializers.CharField()
    poster_url = serializers.CharField()
    genres = serializers.ListField()
    score = serializers.FloatField()
    score_count = serializers.IntegerField()
    age_rating = serializers.CharField()
    studios = serializers.ListField()
    duration = serializers.IntegerField()
    episodes = serializers.IntegerField()
    episodes_aired = serializers.IntegerField()
    fandubbers = serializers.ListField()
    fansubbers = serializers.ListField()
    release_date = serializers.CharField()
    status = serializers.CharField()
    related_material = serializers.ListField()
    trailer_url = serializers.CharField()
