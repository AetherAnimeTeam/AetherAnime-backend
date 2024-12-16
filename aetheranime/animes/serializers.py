from rest_framework import serializers
from .models import Anime, Genre, AnimePreview


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class AnimePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimePreview
        fields = ["anime_id", "name_ru", "poster_url", "score", "status"]


class AnimeSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)

    class Meta:
        model = Anime
        fields = [
            "name_ru",
            "name_original",
            "description",
            "poster_url",
            "genres",
            "score",
            "score_count",
            "age_rating",
            "studios",
            "duration",
            "episodes",
            "episodes_aired",
            "fandubbers",
            "fansubbers",
            "release_date",
            "status",
            "related_material",
            "trailer_url",
        ]

    def create(self, validated_data):
        genres_data = validated_data.pop("genres")
        anime = Anime.objects.create(**validated_data)
        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(**genre_data)
            anime.genres.add(genre)
        return anime
