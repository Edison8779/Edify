"""
Song Model
"""
import uuid
from typing import TYPE_CHECKING, List
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import EdifyBase, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.artist import Artist
    from app.models.genre import Genre
    from app.models.song_variant import SongAudioVariant


class Song(EdifyBase, SoftDeleteMixin):
    __tablename__ = "songs"

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    artist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("artists.id", ondelete="CASCADE"), index=True, nullable=False)
    album_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("albums.id", ondelete="SET NULL"), index=True, nullable=True)
    genre_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("genres.id", ondelete="SET NULL"), index=True, nullable=True)

    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    track_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="audio/mpeg", nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    play_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    artist: Mapped["Artist"] = relationship(back_populates="songs")
    album: Mapped["Album | None"] = relationship(back_populates="songs")
    genre: Mapped["Genre | None"] = relationship(back_populates="songs")
    variants: Mapped[List["SongAudioVariant"]] = relationship(back_populates="song", cascade="all, delete-orphan")
