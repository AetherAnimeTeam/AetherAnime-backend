# Generated by Django 5.1.4 on 2024-12-15 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnimePreview",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("anime_id", models.PositiveIntegerField(unique=True)),
                ("name_ru", models.CharField(max_length=255)),
                ("poster_url", models.URLField()),
                ("score", models.FloatField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ANONS", "Анонсирован"),
                            ("ONGOING", "Онгоинг"),
                            ("RELEASED", "Вышел"),
                        ],
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                ("id", models.PositiveIntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Anime",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name_ru", models.CharField(max_length=255)),
                ("name_original", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("poster_url", models.URLField()),
                ("score", models.FloatField()),
                ("score_count", models.PositiveIntegerField()),
                ("age_rating", models.CharField(max_length=20)),
                ("studios", models.CharField(max_length=255)),
                ("duration", models.PositiveIntegerField()),
                ("episodes", models.PositiveIntegerField()),
                ("episodes_aired", models.PositiveIntegerField()),
                ("fandubbers", models.JSONField(default=list)),
                ("fansubbers", models.JSONField(default=list)),
                ("release_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ANONS", "Анонсирован"),
                            ("ONGOING", "Онгоинг"),
                            ("RELEASED", "Вышел"),
                        ],
                        max_length=20,
                    ),
                ),
                ("related_material", models.JSONField(blank=True, null=True)),
                ("trailer_url", models.URLField(blank=True, null=True)),
                (
                    "genres",
                    models.ManyToManyField(related_name="animes", to="animes.genre"),
                ),
            ],
        ),
    ]
