"""
Song Schemas
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.album import AlbumResponse
from app.schemas.artist import ArtistResponse
from app.schemas.genre import GenreResponse


class SongVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    song_id: uuid.UUID
    quality: str
    file_path: str
    bitrate: int
    codec: str
    file_size_bytes: int
    status: str
    created_at: datetime
    updated_at: datetime


class SongCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    artist_id: uuid.UUID
    album_id: uuid.UUID | None = None
    genre_id: uuid.UUID | None = None
    track_number: int | None = Field(default=None, ge=1)


class SongUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    artist_id: uuid.UUID | None = None
    album_id: uuid.UUID | None = None
    genre_id: uuid.UUID | None = None
    track_number: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class SongResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    artist_id: uuid.UUID
    album_id: uuid.UUID | None = None
    genre_id: uuid.UUID | None = None

    artist: ArtistResponse | None = None
    album: AlbumResponse | None = None
    genre: GenreResponse | None = None

    duration_seconds: int
    track_number: int | None = None

    file_path: str
    original_filename: str
    mime_type: str
    file_size_bytes: int

    is_active: bool
    play_count: int

    variants: list[SongVariantResponse] = []

    created_at: datetime
    updated_at: datetime
