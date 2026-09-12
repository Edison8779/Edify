"""
Song Audio Variant Model
"""
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import EdifyBase

if TYPE_CHECKING:
    from app.models.song import Song


class SongAudioVariant(EdifyBase):
    __tablename__ = "song_audio_variants"

    song_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("songs.id", ondelete="CASCADE"), index=True, nullable=False)
    quality: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # 64k, 128k, 256k
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    bitrate: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., 64000
    codec: Mapped[str] = mapped_column(String(50), default="mp3", nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True, nullable=False)  # pending, processing, ready, failed

    song: Mapped["Song"] = relationship(back_populates="variants")
