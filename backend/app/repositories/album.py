"""
Album Repository
"""
import uuid
from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.album import Album


class AlbumRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, album_id: uuid.UUID) -> Optional[Album]:
        result = await self.session.execute(
            select(Album)
            .options(selectinload(Album.artist))
            .where(Album.id == album_id, Album.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        artist_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[Album], int]:
        query = select(Album).options(selectinload(Album.artist)).where(Album.deleted_at.is_(None))

        if artist_id:
            query = query.where(Album.artist_id == artist_id)
        if search:
            query = query.where(Album.title.ilike(f"%{search}%"))

        count_res = await self.session.execute(select(func.count()).select_from(query.subquery()))
        total = count_res.scalar() or 0

        query = query.order_by(Album.title).offset((page - 1) * page_size).limit(page_size)
        res = await self.session.execute(query)
        return res.scalars().all(), total

    async def create(
        self,
        title: str,
        artist_id: uuid.UUID,
        cover_url: Optional[str] = None,
        release_year: Optional[int] = None,
    ) -> Album:
        album = Album(title=title, artist_id=artist_id, cover_url=cover_url, release_year=release_year)
        self.session.add(album)
        await self.session.flush()
        return album

    async def update(self, album: Album) -> Album:
        self.session.add(album)
        await self.session.flush()
        return album

    async def soft_delete(self, album: Album) -> None:
        import datetime
        album.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        self.session.add(album)
        await self.session.flush()
