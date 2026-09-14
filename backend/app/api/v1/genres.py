"""
Genres Router
"""
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_admin
from app.dependencies.music import get_music_service
from app.models.user import User
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.genre import GenreCreate, GenreResponse
from app.services.music.service import MusicService

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("", response_model=PaginatedResponse[GenreResponse])
async def list_genres(
    music_service: Annotated[MusicService, Depends(get_music_service)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> PaginatedResponse[GenreResponse]:
    genres, total = await music_service.list_genres(page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        data=[GenreResponse.model_validate(g) for g in genres],
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
    )


@router.post("", response_model=DataResponse[GenreResponse], status_code=201)
async def create_genre(
    data: GenreCreate,
    music_service: Annotated[MusicService, Depends(get_music_service)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> DataResponse[GenreResponse]:
    genre = await music_service.create_genre(
        name=data.name, slug=data.slug, description=data.description, actor=current_admin
    )
    return DataResponse(data=GenreResponse.model_validate(genre))


@router.delete("/{genre_id}", status_code=204)
async def delete_genre(
    genre_id: uuid.UUID,
    music_service: Annotated[MusicService, Depends(get_music_service)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> None:
    await music_service.delete_genre(genre_id=genre_id, actor=current_admin)
