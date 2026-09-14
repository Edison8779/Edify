"""
Artists Router
"""
import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_admin
from app.dependencies.music import get_music_service
from app.models.user import User
from app.schemas.artist import ArtistCreate, ArtistResponse, ArtistUpdate
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.services.music.service import MusicService

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.get("", response_model=PaginatedResponse[ArtistResponse])
async def list_artists(
    music_service: Annotated[MusicService, Depends(get_music_service)],
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> PaginatedResponse[ArtistResponse]:
    artists, total = await music_service.list_artists(search=search, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        data=[ArtistResponse.model_validate(a) for a in artists],
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
    )


@router.get("/{artist_id}", response_model=DataResponse[ArtistResponse])
async def get_artist(
    artist_id: uuid.UUID,
    music_service: Annotated[MusicService, Depends(get_music_service)],
) -> DataResponse[ArtistResponse]:
    artist = await music_service.get_artist(artist_id)
    return DataResponse(data=ArtistResponse.model_validate(artist))


@router.post("", response_model=DataResponse[ArtistResponse], status_code=201)
async def create_artist(
    name: str = Form(...),
    bio: Optional[str] = Form(default=None),
    avatar_file: Optional[UploadFile] = File(default=None),
    music_service: Annotated[MusicService, Depends(get_music_service)] = None,
    current_admin: Annotated[User, Depends(require_admin)] = None,
) -> DataResponse[ArtistResponse]:
    artist = await music_service.create_artist(
        name=name, bio=bio, avatar_file=avatar_file, actor=current_admin
    )
    return DataResponse(data=ArtistResponse.model_validate(artist))


@router.put("/{artist_id}", response_model=DataResponse[ArtistResponse])
async def update_artist(
    artist_id: uuid.UUID,
    name: Optional[str] = Form(default=None),
    bio: Optional[str] = Form(default=None),
    avatar_file: Optional[UploadFile] = File(default=None),
    music_service: Annotated[MusicService, Depends(get_music_service)] = None,
    current_admin: Annotated[User, Depends(require_admin)] = None,
) -> DataResponse[ArtistResponse]:
    artist = await music_service.update_artist(
        artist_id=artist_id, name=name, bio=bio, avatar_file=avatar_file, actor=current_admin
    )
    return DataResponse(data=ArtistResponse.model_validate(artist))


@router.delete("/{artist_id}", status_code=204)
async def delete_artist(
    artist_id: uuid.UUID,
    music_service: Annotated[MusicService, Depends(get_music_service)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> None:
    await music_service.delete_artist(artist_id=artist_id, actor=current_admin)
