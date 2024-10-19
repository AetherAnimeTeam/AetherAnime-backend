import aiohttp

from models.anime import Anime, AnimePreview


# Shikimori

def generate_graphql_request(endpoint: str, params: dict, selected_rows: list[str]):
    params = ", ".join(f'{key}:{value}' for key, value in params.items())
    base = f"{endpoint}({params})"
    row_selection = f"{{{'\n'.join(selected_rows)}}}"
    return f"{{{base + row_selection}}}"

async def get_animes_by_name(name: str, order: str = "popularity", status: str = "latest",
                   limit: int = 10, page: int = 1) -> list[AnimePreview]:
    graphql_body = generate_graphql_request("animes",
                                            {"search": f"\"{name}\"", "limit": limit, "page": page,
                                             "order": order, "status": f"\"{status}\""},
                                            ["russian", "poster { id originalUrl }", "score", "status", "id"])

    headers = { "User-Agent": "AetherAnime/1.0" }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post("https://shikimori.one/api/graphql", json={"query": graphql_body}) as response:
            return [AnimePreview(anime_json)
                    for anime_json in (await response.json())["data"]["animes"]]

async def get_details(anime_id: int) -> Anime:
    graphql_body = generate_graphql_request("animes",
                                            {"ids": f"\"{anime_id}\"", "limit": 1,  "page": 1},
                                            ["name", "russian", "description", "poster { id originalUrl }",
                                             "genres { id russian }", "score", "rating", "duration", "episodes",
                                             "episodesAired", "releasedOn { year month day date }", "status"])

    headers = {"User-Agent": "AetherAnime/1.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post("https://shikimori.one/api/graphql", json={"query": graphql_body}) as response:
            return Anime((await response.json())["data"]["animes"][0])