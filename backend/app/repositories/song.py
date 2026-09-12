"""
Song Repository
"""
import uuid
from typing import Optional, Sequence
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.song import Song
from app.models.song_variant import SongAudioVariant


class SongRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, song_id: uuid.UUID) -> Optional[Song]:
        result = await self.session.execute(
            select(Song)
            .options(
                selectinload(Song.artist),
                selectinload(Song.album),
                selectinload(Song.genre),
                selectinload(Song.variants),
            )
            .where(Song.id == song_id, Song.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        artist_id: Optional[uuid.UUID] = None,
        album_id: Optional[uuid.UUID] = None,
        genre_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[Song], int]:
        query = (
            select(Song)
            .options(
                selectinload(Song.artist),
                selectinload(Song.album),
                selectinload(Song.genre),
                selectinload(Song.variants),
            )
            .where(Song.deleted_at.is_(None))
        )

        if is_active is not None:
            query = query.where(Song.is_active == is_active)
        if artist_id:
            query = query.where(Song.artist_id == artist_id)
        if album_id:
            query = query.where(Song.album_id == album_id)
        if genre_id:
            query = query.where(Song.genre_id == genre_id)
        if search:
            query = query.where(Song.title.ilike(f"%{search}%"))

        count_res = await self.session.execute(select(func.count()).select_from(query.subquery()))
        total = count_res.scalar() or 0

        query = query.order_by(Song.title).offset((page - 1) * page_size).limit(page_size)
        res = await self.session.execute(query)
        return res.scalars().all(), total

    async def create(
        self,
        title: str,
        artist_id: uuid.UUID,
        file_path: str,
        original_filename: str,
        mime_type: str,
        file_size_bytes: int,
        duration_seconds: int = 0,
        album_id: Optional[uuid.UUID] = None,
        genre_id: Optional[uuid.UUID] = None,
        track_number: Optional[int] = None,
    ) -> Song:
        song = Song(
            title=title,
            artist_id=artist_id,
            album_id=album_id,
            genre_id=genre_id,
            duration_seconds=duration_seconds,
            track_number=track_number,
            file_path=file_path,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
        )
        self.session.add(song)
        await self.session.flush()
        return song

    async def update(self, song: Song) -> Song:
        self.session.add(song)
        await self.session.flush()
        return song

    async def increment_play_count(self, song_id: uuid.UUID) -> None:
        await self.session.execute(
            update(Song).where(Song.id == song_id).values(play_count=Song.play_count + 1)
        )
        await self.session.flush()

    async def soft_delete(self, song: Song) -> None:
        import datetime
        song.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        self.session.add(song)
        await self.session.flush()

    async def create_variant(
        self,
        song_id: uuid.UUID,
        quality: str,
        file_path: str,
        bitrate: int,
        codec: str,
        file_size_bytes: int,
        status: str = "pending",
    ) -> SongAudioVariant:
        variant = SongAudioVariant(
            song_id=song_id,
            quality=quality,
            file_path=file_path,
            bitrate=bitrate,
            codec=codec,
            file_size_bytes=file_size_bytes,
            status=status,
        )
        self.session.add(variant)
        await self.session.flush()
        return variant

    async def update_variant_status(
        self, variant_id: uuid.UUID, status: str, file_size_bytes: Optional[int] = None
    ) -> None:
        values = {"status": status}
        if file_size_bytes is not None:
            values["file_size_bytes"] = file_size_bytes
        await self.session.execute(
            update(SongAudioVariant).where(SongAudioVariant.id == variant_id).values(**values)
        )
        await self.session.flush()

    async def get_variant_by_quality(self, song_id: uuid.UUID, quality: str) -> Optional[SongAudioVariant]:
        res = await self.session.execute(
            select(SongAudioVariant).where(
                SongAudioVariant.song_id == song_id, SongAudioVariant.quality == quality
            )
        )
        return res.scalar_one_or_none()
