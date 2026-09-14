"""
Albums Router
"""
import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.dependencies.auth import require_admin
from app.dependencies.music import get_music_service
from app.models.user import User
from app.schemas.album import AlbumResponse
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.services.music.service import MusicService

router = APIRouter(prefix="/albums", tags=["Albums"])


@router.get("", response_model=PaginatedResponse[AlbumResponse])
async def list_albums(
    music_service: Annotated[MusicService, Depends(get_music_service)],
    artist_id: Optional[uuid.UUID] = Query(default=None),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> PaginatedResponse[AlbumResponse]:
    albums, total = await music_service.list_albums(
        artist_id=artist_id, search=search, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        data=[AlbumResponse.model_validate(a) for a in albums],
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
    )


@router.get("/{album_id}", response_model=DataResponse[AlbumResponse])
async def get_album(
    album_id: uuid.UUID,
    music_service: Annotated[MusicService, Depends(get_music_service)],
) -> DataResponse[AlbumResponse]:
    album = await music_service.get_album(album_id)
    return DataResponse(data=AlbumResponse.model_validate(album))


@router.post("", response_model=DataResponse[AlbumResponse], status_code=201)
async def create_album(
    title: str = Form(...),
    artist_id: uuid.UUID = Form(...),
    release_year: Optional[int] = Form(default=None),
    cover_file: Optional[UploadFile] = File(default=None),
    music_service: Annotated[MusicService, Depends(get_music_service)] = None,
    current_admin: Annotated[User, Depends(require_admin)] = None,
) -> DataResponse[AlbumResponse]:
    album = await music_service.create_album(
        title=title,
        artist_id=artist_id,
        cover_file=cover_file,
        release_year=release_year,
        actor=current_admin,
    )
    return DataResponse(data=AlbumResponse.model_validate(album))
