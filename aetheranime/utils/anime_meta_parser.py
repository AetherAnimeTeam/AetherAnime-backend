import asyncio
from typing import Optional

import aiohttp
import requests

from animes.serializers import AnimeSerializer
from animes.models import Anime, AnimePreview

# Shikimori


def generate_graphql_request(endpoint: str, params: dict, selected_rows: list[str]):
    params = ", ".join(f"{key}:{value}" for key, value in params.items())
    base = f"{endpoint}({params})"
    row_selection = "{" + "\n".join(selected_rows) + "}"
    return f"{{{base + row_selection}}}"


def get_animes_by_name(
    name: Optional[str] = None,
    order: str = "popularity",
    status: Optional[str] = None,
    limit: int = 10,
    page: int = 1,
) -> list[AnimePreview]:
    params = {
            "limit": limit,
            "page": page,
            "order": order,
        }

    if name: params["search"] = f'"{name}"'
    if status: params["status"] = f'"{status}"'

    graphql_body = generate_graphql_request(
        "animes",
        params,
        ["russian", "poster { originalUrl }", "score", "status", "id"],
    )

    headers = {"User-Agent": "AetherAnime/1.0"}

    response = requests.post(
        "https://shikimori.one/api/graphql",
        json={"query": graphql_body},
        headers=headers,
    )

    return [
        anime_json for anime_json in (response.json())["data"]["animes"]
    ]


def save_anime_to_db(anime_data: dict) -> Anime:
    serializer = AnimeSerializer(data=anime_data)
    if serializer.is_valid():
        return serializer.save()
    else:
        raise ValueError(f"Invalid data: {serializer.errors}")


def get_details(anime_id: int) -> Anime:
    graphql_body = generate_graphql_request(
        "animes",
        {"ids": f'"{anime_id}"', "limit": 1, "page": 1},
        [
            "name",
            "russian",
            "description",
            "poster { id originalUrl }",
            "genres { id russian }",
            "score",
            "scoresStats {count score}",
            "rating",
            "duration",
            "episodes",
            "episodesAired",
            "releasedOn { date }",
            "airedOn { date }",
            "status",
            "studios { name }",
            "fandubbers",
            "fansubbers",
        ],
    )

    headers = {"User-Agent": "AetherAnime/1.0"}

    response = requests.post(
        "https://shikimori.one/api/graphql",
        json={"query": graphql_body},
        headers=headers,
    )

    anime_data = (response.json())["data"]["animes"][0]
    # return anime_data
    adapted_anime_data = {
        "name_ru": anime_data["russian"],
        "name_original": anime_data["name"],
        "description": anime_data.get("description", "Описание отсутствует"),
        "poster_url": anime_data["poster"]["originalUrl"],
        "genres": [{"id": g["id"], "name": g["russian"]} for g in anime_data["genres"]],
        "score": anime_data["score"],
        "score_count": sum(stat["count"] for stat in anime_data["scoresStats"]),
        "age_rating": anime_data["rating"],
        "duration": anime_data["duration"],
        "episodes": anime_data["episodes"],
        "episodes_aired": anime_data["episodesAired"],
        "studios": ", ".join([studio["name"] for studio in anime_data["studios"]]),
        "fandubbers": anime_data["fandubbers"],
        "fansubbers": anime_data["fansubbers"],
        "release_date": anime_data["releasedOn"]["date"],
        "aired_on": anime_data["airedOn"]["date"],
        "status": anime_data["status"],
        "related_material": None,
        "trailer_url": None,
    }

    # return anime_data
    return save_anime_to_db(adapted_anime_data)
