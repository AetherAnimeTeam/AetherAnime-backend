# Generated by Django 5.1.4 on 2025-01-27 10:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0004_alter_customuser_managers"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnimeRating",
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
                ("anime_id", models.BigIntegerField()),
                ("score", models.PositiveSmallIntegerField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ratings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "anime_id")},
            },
        ),
    ]
