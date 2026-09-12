"""
Genre Repository
"""
import uuid
from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.genre import Genre


class GenreRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, genre_id: uuid.UUID) -> Optional[Genre]:
        result = await self.session.execute(select(Genre).where(Genre.id == genre_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Genre]:
        result = await self.session.execute(select(Genre).where(Genre.slug == slug))
        return result.scalar_one_or_none()

    async def list_all(self, page: int = 1, page_size: int = 50) -> tuple[Sequence[Genre], int]:
        count_res = await self.session.execute(select(func.count(Genre.id)))
        total = count_res.scalar() or 0

        query = select(Genre).order_by(Genre.name).offset((page - 1) * page_size).limit(page_size)
        res = await self.session.execute(query)
        return res.scalars().all(), total

    async def create(self, name: str, slug: str, description: Optional[str] = None) -> Genre:
        genre = Genre(name=name, slug=slug, description=description)
        self.session.add(genre)
        await self.session.flush()
        return genre

    async def delete(self, genre: Genre) -> None:
        await self.session.delete(genre)
        await self.session.flush()
