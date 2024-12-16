from django.db import models
from django.conf import settings


class Comment(models.Model):
    anime_id = models.IntegerField()
    reply_to = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class WatchedHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    anime_id = models.IntegerField()
    season = models.IntegerField()
    episode = models.IntegerField()
    timestamp = models.DateTimeField()


class Status(models.TextChoices):
    WATCHED = "watched", "Просмотрено"
    PLANNED = "planned", "В планах"
    WATCHING = "watching", "Смотрю"
    PAUSED = "paused", "Отложено"
    DROPPED = "dropped", "Брошено"


class AnimeStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    anime_id = models.IntegerField()
    status = models.CharField(max_length=10, choices=Status.choices)


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    anime_id = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
