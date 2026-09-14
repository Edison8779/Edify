"""
Songs Router
"""
import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, Request, Response, UploadFile

from app.core.exceptions import ValidationException
from app.dependencies.auth import get_current_user, require_admin
from app.dependencies.music import get_music_service, get_streaming_service
from app.models.user import User
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.song import SongResponse, SongUpdate
from app.services.music.service import MusicService
from app.services.streaming.service import StreamingService

router = APIRouter(prefix="/songs", tags=["Songs"])


@router.get("", response_model=PaginatedResponse[SongResponse])
async def list_songs(
    music_service: Annotated[MusicService, Depends(get_music_service)],
    artist_id: Optional[uuid.UUID] = Query(default=None),
    album_id: Optional[uuid.UUID] = Query(default=None),
    genre_id: Optional[uuid.UUID] = Query(default=None),
    search: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> PaginatedResponse[SongResponse]:
    songs, total = await music_service.list_songs(
        artist_id=artist_id,
        album_id=album_id,
        genre_id=genre_id,
        search=search,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        data=[SongResponse.model_validate(s) for s in songs],
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
    )


@router.get("/{song_id}", response_model=DataResponse[SongResponse])
async def get_song(
    song_id: uuid.UUID,
    music_service: Annotated[MusicService, Depends(get_music_service)],
) -> DataResponse[SongResponse]:
    song = await music_service.get_song(song_id)
    return DataResponse(data=SongResponse.model_validate(song))


@router.get("/{song_id}/stream")
async def stream_song(
    song_id: uuid.UUID,
    request: Request,
    quality: Optional[str] = Query(default=None),
    streaming_service: Annotated[StreamingService, Depends(get_streaming_service)] = None,
) -> Response:
    return await streaming_service.get_stream_response(song_id=song_id, quality=quality, request=request)


@router.post("/upload", response_model=DataResponse[SongResponse], status_code=201)
async def upload_song(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    artist_id: uuid.UUID = Form(...),
    audio_file: UploadFile = File(...),
    album_id: Optional[uuid.UUID] = Form(default=None),
    genre_id: Optional[uuid.UUID] = Form(default=None),
    track_number: Optional[int] = Form(default=None),
    duration_seconds: Optional[int] = Form(default=180),
    cover_file: Optional[UploadFile] = File(default=None),
    music_service: Annotated[MusicService, Depends(get_music_service)] = None,
    current_admin: Annotated[User, Depends(require_admin)] = None,
) -> DataResponse[SongResponse]:
    # Debug logging of received form fields
    logger = music_service.logger if hasattr(music_service, "logger") else None
    if logger:
        logger.info(
            "upload_song_received",
            title=title,
            artist_id=str(artist_id),
            album_id=str(album_id) if album_id else None,
            genre_id=str(genre_id) if genre_id else None,
            track_number=track_number,
            duration_seconds=duration_seconds,
        )
    else:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info(
            "upload_song_received",
            title=title,
            artist_id=str(artist_id),
            album_id=str(album_id) if album_id else None,
            genre_id=str(genre_id) if genre_id else None,
            track_number=track_number,
            duration_seconds=duration_seconds,
        )
    song = await music_service.upload_song(
        title=title,
        artist_id=artist_id,
        audio_file=audio_file,
        album_id=album_id,
        genre_id=genre_id,
        track_number=track_number,
        duration_seconds=duration_seconds or 180,
        cover_file=cover_file,
        background_tasks=background_tasks,
        actor=current_admin,
    )
    return DataResponse(data=SongResponse.model_validate(song))




@router.put("/{song_id}", response_model=DataResponse[SongResponse])
async def update_song(
    song_id: uuid.UUID,
    data: SongUpdate,
    music_service: Annotated[MusicService, Depends(get_music_service)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> DataResponse[SongResponse]:
    song = await music_service.update_song(
        song_id=song_id,
        title=data.title,
        artist_id=data.artist_id,
        album_id=data.album_id,
        genre_id=data.genre_id,
        track_number=data.track_number,
        is_active=data.is_active,
        actor=current_admin,
    )
    return DataResponse(data=SongResponse.model_validate(song))


@router.delete("/{song_id}", status_code=204)
async def delete_song(
    song_id: uuid.UUID,
    music_service: Annotated[MusicService, Depends(get_music_service)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> None:
    await music_service.delete_song(song_id=song_id, actor=current_admin)
