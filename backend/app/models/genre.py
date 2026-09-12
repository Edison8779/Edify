"""
Genre Model
"""
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import EdifyBase

if TYPE_CHECKING:
    from app.models.song import Song


class Genre(EdifyBase):
    __tablename__ = "genres"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    songs: Mapped[List["Song"]] = relationship(back_populates="genre")
