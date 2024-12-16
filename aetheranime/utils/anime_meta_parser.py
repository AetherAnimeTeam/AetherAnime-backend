import aiohttp

from animes.serializers import AnimeSerializer
from animes.models import Anime, AnimePreview


# Shikimori


def generate_graphql_request(endpoint: str, params: dict, selected_rows: list[str]):
    params = ", ".join(f"{key}:{value}" for key, value in params.items())
    base = f"{endpoint}({params})"
    row_selection = "{" + "\n".join(selected_rows) + "}"
    return f"{{{base + row_selection}}}"


async def get_animes_by_name(
    name: str,
    order: str = "popularity",
    status: str = "latest",
    limit: int = 10,
    page: int = 1,
) -> list[AnimePreview]:
    graphql_body = generate_graphql_request(
        "animes",
        {
            "search": f'"{name}"',
            "limit": limit,
            "page": page,
            "order": order,
            "status": f'"{status}"',
        },
        ["russian", "poster { id originalUrl }", "score", "status", "id"],
    )

    headers = {"User-Agent": "AetherAnime/1.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            "https://shikimori.one/api/graphql", json={"query": graphql_body}
        ) as response:
            return [
                AnimePreview(anime_json)
                for anime_json in (await response.json())["data"]["animes"]
            ]


async def save_anime_to_db(anime_data: dict) -> Anime:
    serializer = AnimeSerializer(data=anime_data)
    if serializer.is_valid():
        return serializer.save()
    else:
        raise ValueError(f"Invalid data: {serializer.errors}")


async def get_details(anime_id: int) -> Anime:
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
            "releasedOn",
            "status",
            "studios { name }",
            "fandubbers",
            "fansubbers",
        ],
    )

    headers = {"User-Agent": "AetherAnime/1.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            "https://shikimori.one/api/graphql", json={"query": graphql_body}
        ) as response:
            anime_data = (await response.json())["data"]["animes"][0]

            adapted_anime_data = {
                "name_ru": anime_data["russian"],
                "name_original": anime_data["name"],
                "description": anime_data.get("description", "Описание отсутствует"),
                "poster_url": anime_data["poster"]["originalUrl"],
                "genres": [
                    {"id": g["id"], "name": g["russian"]} for g in anime_data["genres"]
                ],
                "score": anime_data["score"],
                "score_count": sum(stat["count"] for stat in anime_data["scoresStats"]),
                "age_rating": anime_data["rating"],
                "duration": anime_data["duration"],
                "episodes": anime_data["episodes"],
                "episodes_aired": anime_data["episodesAired"],
                "studios": ", ".join(
                    [studio["name"] for studio in anime_data["studios"]]
                ),
                "fandubbers": anime_data["fandubbers"],
                "fansubbers": anime_data["fansubbers"],
                "release_date": anime_data["releasedOn"],
                "status": anime_data["status"],
                "related_material": None,
                "trailer_url": None,
            }
            return await save_anime_to_db(adapted_anime_data)
