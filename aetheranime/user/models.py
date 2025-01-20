from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


class CustomUser(AbstractUser):
    username = models.CharField(max_length=30, unique=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
    )
    email = models.EmailField(
        unique=True,
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verified User",
    )
    tag = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.username

    def generate_unique_tag(self):
        while True:
            tag = "".join(random.choices(string.digits, k=4))
            if not CustomUser.objects.filter(tag=tag).exists():
                return tag

    def save(self, *args, **kwargs):
        if not self.tag:
            self.tag = self.generate_unique_tag()
        super().save(*args, **kwargs)

    def deactivate(self):
        """
        Деактивирует аккаунт пользователя.
        """
        self.is_active = False
        self.save()


class History(models.Model):
    anime_id = models.BigIntegerField()
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="histories",
    )
    time = models.DateTimeField()
    season = models.SmallIntegerField()
    episode = models.IntegerField()

    def __str__(self):
        return f"History of {self.user} for anime {self.anime_id}"


class Status(models.Model):
    STATUS_CHOICES = [
        ("watching", "Watching"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
        ("dropped", "Dropped"),
        ("plan_to_watch", "Plan to Watch"),
    ]
    anime_id = models.BigIntegerField()
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="statuses",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Status of {self.user} for anime {self.anime_id}"


class Review(models.Model):
    anime_id = models.BigIntegerField()
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    text = models.TextField(null=True, blank=True)
    score = models.BigIntegerField()

    def __str__(self):
        return f"Review by {self.user} for anime {self.anime_id}"


class Comment(models.Model):
    anime_id = models.BigIntegerField()
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField()
    likes = models.BigIntegerField(default=0)
    dislikes = models.BigIntegerField(default=0)
    reply_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    def __str__(self):
        return f"Comment by {self.user} for anime {self.anime_id}"
