from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from anime_meta_parser import get_animes_by_name, get_details

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешённые домены
    allow_credentials=True,  # Если требуется отправка куки
    allow_methods=["*"],     # Разрешённые методы (GET, POST, и т.д.)
    allow_headers=["*"],     # Разрешённые заголовки
)

real_debrid_api = "YOJ7JRE25K5DVPRDEO3VXNMY5UNUQHN5RYUWDZ3Y7JPQVQC2TANAtorrentio"
# anime_finder = AnimeFinder(TorrentEngines.NM_CLUB.value)

@app.get("/")
async def root():
    return {"status": "Active"}


@app.get("/search/")
async def search_anime(name: str, order: str = "popularity", status: str = "",
                       limit: int = 10, page: int = 1):
    return await get_animes_by_name(name, status=status, order=order, limit=limit, page=page)

@app.get("/popular/")
async def popular_anime(limit: int = 10, page: int = 1):
    return await get_animes_by_name("", limit=limit, page=page)

@app.get("/detailed/")
async def detailed_meta(anime_id: int):
    return await get_details(anime_id)

@app.get("/magnet/{name}")
async def search_magnet(name: str):
    # animes = await anime_finder.search(name.encode("utf-8").decode("utf-8"))
    return {"list": []}

