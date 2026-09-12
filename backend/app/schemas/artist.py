"""
Artist Schemas
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ArtistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    bio: str | None = None
    avatar_url: str | None = None


class ArtistUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    bio: str | None = None
    avatar_url: str | None = None


class ArtistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    bio: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime
