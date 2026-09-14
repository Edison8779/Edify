"""
Album Model
"""
import uuid
from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import EdifyBase, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.artist import Artist
    from app.models.song import Song


class Album(EdifyBase, SoftDeleteMixin):
    __tablename__ = "albums"

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    artist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("artists.id", ondelete="CASCADE"), index=True, nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    artist: Mapped["Artist"] = relationship(back_populates="albums")
    songs: Mapped[List["Song"]] = relationship(back_populates="album", cascade="all, delete-orphan")
