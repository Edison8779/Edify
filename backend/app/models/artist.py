"""
Artist Model
"""
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import EdifyBase, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.song import Song


class Artist(EdifyBase, SoftDeleteMixin):
    __tablename__ = "artists"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    albums: Mapped[List["Album"]] = relationship(back_populates="artist", cascade="all, delete-orphan")
    songs: Mapped[List["Song"]] = relationship(back_populates="artist", cascade="all, delete-orphan")
