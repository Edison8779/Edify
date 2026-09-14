"""
Search Router
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.dependencies.music import get_music_service
from app.schemas.album import AlbumResponse
from app.schemas.artist import ArtistResponse
from app.schemas.common import DataResponse
from app.schemas.song import SongResponse
from app.services.music.service import MusicService

router = APIRouter(prefix="/search", tags=["Search"])


class SearchResult(BaseModel):
    songs: list[SongResponse] = []
    artists: list[ArtistResponse] = []
    albums: list[AlbumResponse] = []


@router.get("", response_model=DataResponse[SearchResult])
async def global_search(
    q: str = Query(min_length=1),
    music_service: Annotated[MusicService, Depends(get_music_service)] = None,
) -> DataResponse[SearchResult]:
    songs, _ = await music_service.list_songs(search=q, page=1, page_size=10)
    artists, _ = await music_service.list_artists(search=q, page=1, page_size=10)
    albums, _ = await music_service.list_albums(search=q, page=1, page_size=10)

    result = SearchResult(
        songs=[SongResponse.model_validate(s) for s in songs],
        artists=[ArtistResponse.model_validate(a) for a in artists],
        albums=[AlbumResponse.model_validate(al) for al in albums],
    )
    return DataResponse(data=result)
