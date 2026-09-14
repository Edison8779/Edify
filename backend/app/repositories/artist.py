"""
Artist Repository
"""
import uuid
from typing import Optional, Sequence
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.artist import Artist


class ArtistRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, artist_id: uuid.UUID) -> Optional[Artist]:
        result = await self.session.execute(
            select(Artist).where(Artist.id == artist_id, Artist.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_all(
        self, search: Optional[str] = None, page: int = 1, page_size: int = 50
    ) -> tuple[Sequence[Artist], int]:
        query = select(Artist).where(Artist.deleted_at.is_(None))
        if search:
            query = query.where(Artist.name.ilike(f"%{search}%"))

        count_res = await self.session.execute(select(func.count()).select_from(query.subquery()))
        total = count_res.scalar() or 0

        query = query.order_by(Artist.name).offset((page - 1) * page_size).limit(page_size)
        res = await self.session.execute(query)
        return res.scalars().all(), total

    async def create(
        self, name: str, bio: Optional[str] = None, avatar_url: Optional[str] = None
    ) -> Artist:
        artist = Artist(name=name, bio=bio, avatar_url=avatar_url)
        self.session.add(artist)
        await self.session.flush()
        return artist

    async def update(self, artist: Artist) -> Artist:
        self.session.add(artist)
        await self.session.flush()
        return artist

    async def soft_delete(self, artist: Artist) -> None:
        import datetime
        artist.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        self.session.add(artist)
        await self.session.flush()
