from django.db import models
from enum import Enum


class AnimeStatus(models.TextChoices):
    ANONS = "ANONS", "Анонсирован"
    ONGOING = "ONGOING", "Онгоинг"
    RELEASED = "RELEASED", "Вышел"


class Genre(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AnimePreview(models.Model):
    anime_id = models.PositiveIntegerField(unique=True)
    name_ru = models.CharField(max_length=255)
    poster_url = models.URLField()
    score = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=AnimeStatus.choices,
    )

    def __str__(self):
        return self.name_ru


class Anime(models.Model):
    name_ru = models.CharField(max_length=255)
    name_original = models.CharField(max_length=255)
    description = models.TextField()

    poster_url = models.URLField()
    genres = models.ManyToManyField(Genre, related_name="animes")

    score = models.FloatField()
    score_count = models.PositiveIntegerField()
    age_rating = models.CharField(max_length=20)

    studios = models.CharField(max_length=255)
    duration = models.PositiveIntegerField()
    episodes = models.PositiveIntegerField()
    episodes_aired = models.PositiveIntegerField()

    fandubbers = models.JSONField(default=list)
    fansubbers = models.JSONField(default=list)

    release_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=AnimeStatus.choices,
    )

    related_material = models.JSONField(null=True, blank=True)
    trailer_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name_ru
