from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional

# Shikimori based models

class AnimeStatus(Enum):
    ANONS = "Анонсирован"
    ONGOING = "Онгоинг"
    RELEASED = "Вышел"


@dataclass
class Genre:
    id_: int
    name: str

@dataclass
class AnimePreview:
    anime_id: int
    name_ru: str

    poster_url: str
    score: float
    status: AnimeStatus

    def __init__(self, anime_dict):
        self.anime_id = anime_dict["id"]
        self.name_ru = anime_dict["russian"]
        self.poster_url = anime_dict["poster"]["originalUrl"]
        self.score = anime_dict["score"]
        self.status = AnimeStatus[anime_dict["status"].upper()]

@dataclass
class Anime:
    name_ru: str
    name_original: str

    description: str

    poster_url: str

    genres: list[Genre]

    score: float
    age_rating: str

    # TODO: find author and studio
    # author: str
    # studio: str

    duration: int
    episodes: int
    episodes_aired: int
    fandubbers: list[str]
    fansubbers: list[str]

    release_date: datetime
    status: AnimeStatus

    # TODO: refactor related material logic, remove optional
    related_material: Optional[list[str]] = None

    # TODO: remove optional
    trailer_url: Optional[str] = None

    def __init__(self, anime_dict):
        self.name_ru = anime_dict["russian"]
        self.name_original = anime_dict["name"]
        self.description = anime_dict.get("description", "Описание отсутствует")
        self.poster_url = anime_dict["poster"]["originalUrl"]
        self.genres = [Genre(id_=genre["id"], name=genre["russian"])
                  for genre in anime_dict["genres"]]
        self.score = anime_dict["score"]
        self.age_rating = anime_dict["rating"]
        self.duration = anime_dict["duration"]
        self.episodes = anime_dict["episodes"]
        self.episodes_aired = anime_dict["episodesAired"]
        self.fansubbers = anime_dict["fansubbers"]
        self.fandubbers = anime_dict["fandubbers"]
        self.release_date = anime_dict["releasedOn"]
        self.status = AnimeStatus[anime_dict["status"].upper()]

