"""
Album Schemas
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.artist import ArtistResponse


class AlbumCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    artist_id: uuid.UUID
    cover_url: str | None = None
    release_year: int | None = Field(default=None, ge=1800, le=2100)


class AlbumUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    artist_id: uuid.UUID | None = None
    cover_url: str | None = None
    release_year: int | None = Field(default=None, ge=1800, le=2100)


class AlbumResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    artist_id: uuid.UUID
    artist: ArtistResponse | None = None
    cover_url: str | None = None
    release_year: int | None = None
    created_at: datetime
    updated_at: datetime
