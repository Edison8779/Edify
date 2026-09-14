"""
Music Service
"""
import uuid
from typing import Optional, Sequence
from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.album import Album
from app.models.artist import Artist
from app.models.genre import Genre
from app.models.song import Song
from app.models.user import User
from app.repositories.album import AlbumRepository
from app.repositories.artist import ArtistRepository
from app.repositories.genre import GenreRepository
from app.repositories.song import SongRepository
from app.services.audit.service import AuditService
from app.services.music.storage import StorageService
from app.services.music.transcoder import TranscoderService


class MusicService:
    def __init__(
        self,
        session: AsyncSession,
        audit_service: AuditService,
        storage_service: StorageService,
        transcoder_service: TranscoderService,
    ):
        self.session = session
        self.audit_service = audit_service
        self.storage = storage_service
        self.transcoder = transcoder_service

        self.artist_repo = ArtistRepository(session)
        self.album_repo = AlbumRepository(session)
        self.genre_repo = GenreRepository(session)
        self.song_repo = SongRepository(session)

    # ---- Genres ----
    async def create_genre(self, name: str, slug: str | None, description: str | None, actor: User) -> Genre:
        if not slug:
            slug = name.lower().replace(" ", "-")

        existing = await self.genre_repo.get_by_slug(slug)
        if existing:
            raise ValidationException(code="GENRE_EXISTS", message=f"Genre with slug '{slug}' already exists.")

        genre = await self.genre_repo.create(name=name, slug=slug, description=description)

        await self.audit_service.log_action(
            actor_id=actor.id,
            action="GENRE_CREATE",
            target_type="genre",
            target_id=str(genre.id),
            details={"name": genre.name},
        )
        return genre

    async def list_genres(self, page: int = 1, page_size: int = 50) -> tuple[Sequence[Genre], int]:
        return await self.genre_repo.list_all(page=page, page_size=page_size)

    async def delete_genre(self, genre_id: uuid.UUID, actor: User) -> None:
        genre = await self.genre_repo.get_by_id(genre_id)
        if not genre:
            raise NotFoundException(code="GENRE_NOT_FOUND", message=f"Genre {genre_id} not found.")

        await self.genre_repo.delete(genre)
        await self.audit_service.log_action(
            actor_id=actor.id,
            action="GENRE_DELETE",
            target_type="genre",
            target_id=str(genre_id),
        )

    # ---- Artists ----
    async def create_artist(
        self, name: str, bio: str | None = None, avatar_file: UploadFile | None = None, actor: User | None = None
    ) -> Artist:
        avatar_url = None
        artist_id = uuid.uuid4()

        if avatar_file:
            avatar_url = await self.storage.save_cover_image(avatar_file, artist_id)

        artist = await self.artist_repo.create(name=name, bio=bio, avatar_url=avatar_url)

        if actor:
            await self.audit_service.log_action(
                actor_id=actor.id,
                action="ARTIST_CREATE",
                target_type="artist",
                target_id=str(artist.id),
                details={"name": artist.name},
            )
        return artist

    async def list_artists(
        self, search: str | None = None, page: int = 1, page_size: int = 50
    ) -> tuple[Sequence[Artist], int]:
        return await self.artist_repo.list_all(search=search, page=page, page_size=page_size)

    async def get_artist(self, artist_id: uuid.UUID) -> Artist:
        artist = await self.artist_repo.get_by_id(artist_id)
        if not artist:
            raise NotFoundException(code="ARTIST_NOT_FOUND", message=f"Artist {artist_id} not found.")
        return artist

    async def update_artist(
        self,
        artist_id: uuid.UUID,
        name: str | None = None,
        bio: str | None = None,
        avatar_file: UploadFile | None = None,
        actor: User | None = None,
    ) -> Artist:
        artist = await self.get_artist(artist_id)
        if name:
            artist.name = name
        if bio is not None:
            artist.bio = bio
        if avatar_file:
            artist.avatar_url = await self.storage.save_cover_image(avatar_file, artist.id)

        artist = await self.artist_repo.update(artist)

        if actor:
            await self.audit_service.log_action(
                actor_id=actor.id,
                action="ARTIST_UPDATE",
                target_type="artist",
                target_id=str(artist_id),
            )
        return artist

    async def delete_artist(self, artist_id: uuid.UUID, actor: User) -> None:
        artist = await self.get_artist(artist_id)
        await self.artist_repo.soft_delete(artist)

        await self.audit_service.log_action(
            actor_id=actor.id,
            action="ARTIST_DELETE",
            target_type="artist",
            target_id=str(artist_id),
        )

    # ---- Albums ----
    async def create_album(
        self,
        title: str,
        artist_id: uuid.UUID,
        cover_file: UploadFile | None = None,
        release_year: int | None = None,
        actor: User | None = None,
    ) -> Album:
        artist = await self.artist_repo.get_by_id(artist_id)
        if not artist:
            raise NotFoundException(code="ARTIST_NOT_FOUND", message=f"Artist {artist_id} not found.")

        album_id = uuid.uuid4()
        cover_url = None
        if cover_file:
            cover_url = await self.storage.save_cover_image(cover_file, album_id)

        album = await self.album_repo.create(
            title=title, artist_id=artist_id, cover_url=cover_url, release_year=release_year
        )

        if actor:
            await self.audit_service.log_action(
                actor_id=actor.id,
                action="ALBUM_CREATE",
                target_type="album",
                target_id=str(album.id),
                details={"title": album.title},
            )
        return album

    async def list_albums(
        self,
        artist_id: uuid.UUID | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[Album], int]:
        return await self.album_repo.list_all(artist_id=artist_id, search=search, page=page, page_size=page_size)

    async def get_album(self, album_id: uuid.UUID) -> Album:
        album = await self.album_repo.get_by_id(album_id)
        if not album:
            raise NotFoundException(code="ALBUM_NOT_FOUND", message=f"Album {album_id} not found.")
        return album

    # ---- Songs ----
    async def upload_song(
        self,
        title: str,
        artist_id: uuid.UUID,
        audio_file: UploadFile,
        album_id: uuid.UUID | None = None,
        genre_id: uuid.UUID | None = None,
        track_number: int | None = None,
        duration_seconds: int = 180,
        cover_file: UploadFile | None = None,
        background_tasks: BackgroundTasks | None = None,
        actor: User | None = None,
    ) -> Song:
        artist = await self.artist_repo.get_by_id(artist_id)
        if not artist:
            raise NotFoundException(code="ARTIST_NOT_FOUND", message=f"Artist {artist_id} not found.")

        song_id = uuid.uuid4()
        rel_path, file_size = await self.storage.save_audio_file(audio_file, song_id)

        if cover_file and album_id:
            cover_url = await self.storage.save_cover_image(cover_file, album_id)
            album = await self.album_repo.get_by_id(album_id)
            if album:
                album.cover_url = cover_url
                await self.album_repo.update(album)

        mime_type = audio_file.content_type or "audio/mpeg"
        song = await self.song_repo.create(
            title=title,
            artist_id=artist_id,
            album_id=album_id,
            genre_id=genre_id,
            track_number=track_number,
            duration_seconds=duration_seconds,
            file_path=rel_path,
            original_filename=audio_file.filename or "audio.mp3",
            mime_type=mime_type,
            file_size_bytes=file_size,
        )

        await self.session.commit()

        # Trigger background transcoding
        if background_tasks:
            background_tasks.add_task(
                self.transcoder.transcode_song,
                song_id=song.id,
                original_rel_path=rel_path,
            )

        if actor:
            await self.audit_service.log_action(
                actor_id=actor.id,
                action="SONG_UPLOAD",
                target_type="song",
                target_id=str(song.id),
                details={"title": song.title, "filename": song.original_filename},
            )

        full_song = await self.song_repo.get_by_id(song.id)
        return full_song or song

    async def list_songs(
        self,
        artist_id: uuid.UUID | None = None,
        album_id: uuid.UUID | None = None,
        genre_id: uuid.UUID | None = None,
        search: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[Song], int]:
        return await self.song_repo.list_all(
            artist_id=artist_id,
            album_id=album_id,
            genre_id=genre_id,
            search=search,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )

    async def get_song(self, song_id: uuid.UUID) -> Song:
        song = await self.song_repo.get_by_id(song_id)
        if not song:
            raise NotFoundException(code="SONG_NOT_FOUND", message=f"Song {song_id} not found.")
        return song

    async def update_song(
        self,
        song_id: uuid.UUID,
        title: str | None = None,
        artist_id: uuid.UUID | None = None,
        album_id: uuid.UUID | None = None,
        genre_id: uuid.UUID | None = None,
        track_number: int | None = None,
        is_active: bool | None = None,
        actor: User | None = None,
    ) -> Song:
        song = await self.get_song(song_id)
        if title:
            song.title = title
        if artist_id:
            song.artist_id = artist_id
        if album_id is not None:
            song.album_id = album_id
        if genre_id is not None:
            song.genre_id = genre_id
        if track_number is not None:
            song.track_number = track_number
        if is_active is not None:
            song.is_active = is_active

        song = await self.song_repo.update(song)

        if actor:
            await self.audit_service.log_action(
                actor_id=actor.id,
                action="SONG_UPDATE",
                target_type="song",
                target_id=str(song_id),
            )
        return song

    async def delete_song(self, song_id: uuid.UUID, actor: User) -> None:
        song = await self.get_song(song_id)
        await self.song_repo.soft_delete(song)

        await self.audit_service.log_action(
            actor_id=actor.id,
            action="SONG_DELETE",
            target_type="song",
            target_id=str(song_id),
        )
