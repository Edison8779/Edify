"""
Edify Admin & Catalog Seeding Script

Usage:
    python -m app.scripts.seed
"""
import asyncio
import os
import uuid
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger, setup_logging
from app.models.album import Album
from app.models.artist import Artist
from app.models.genre import Genre
from app.models.song import Song
from app.models.user import User
from app.repositories.album import AlbumRepository
from app.repositories.artist import ArtistRepository
from app.repositories.audit import AuditRepository
from app.repositories.genre import GenreRepository
from app.repositories.song import SongRepository
from app.repositories.user import UserRepository
from app.services.audit.service import AuditService
from app.services.auth.password import PasswordAuthService
from app.services.auth.service import AuthService
from app.services.music.storage import StorageService

logger = get_logger(__name__)

DEFAULT_GENRES = [
    {"name": "Pop", "slug": "pop", "description": "Popular music styles"},
    {"name": "Rock", "slug": "rock", "description": "Rock and alternative music"},
    {"name": "Hip Hop", "slug": "hip-hop", "description": "Hip-Hop, Rap and R&B"},
    {"name": "Electronic", "slug": "electronic", "description": "EDM, Ambient and Synthwave"},
    {"name": "Lo-Fi", "slug": "lo-fi", "description": "Chill beats and lo-fi instrumental"},
    {"name": "Classical", "slug": "classical", "description": "Classical and orchestral compositions"},
]


async def seed_data() -> None:
    setup_logging()
    logger.info("starting_seeding_process")

    storage = StorageService()

    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        audit_repo = AuditRepository(session)
        auth_service = AuthService(user_repo)
        audit_service = AuditService(audit_repo)
        pwd_service = PasswordAuthService(user_repo, auth_service, audit_service)

        # 1. Seed Admin Account
        admin_email = os.getenv("ADMIN_EMAIL", "admin@edify.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")

        admin_user = await user_repo.get_by_email(admin_email)
        if not admin_user:
            admin_user, _, _ = await pwd_service.register(
                email=admin_email,
                password=admin_password,
                first_name="Admin",
                last_name="Edify",
            )
            admin_user.is_admin = True
            session.add(admin_user)
            await session.commit()
            logger.info("admin_user_created", email=admin_email)
        else:
            logger.info("admin_user_already_exists", email=admin_email)

        # 2. Seed Standard Genres
        genre_repo = GenreRepository(session)
        seeded_genres = []
        for g_data in DEFAULT_GENRES:
            existing = await genre_repo.get_by_slug(g_data["slug"])
            if not existing:
                genre = await genre_repo.create(
                    name=g_data["name"], slug=g_data["slug"], description=g_data["description"]
                )
                seeded_genres.append(genre)
                logger.info("genre_created", name=g_data["name"])
            else:
                seeded_genres.append(existing)

        # 3. Seed Sample Artist
        artist_repo = ArtistRepository(session)
        artists, _ = await artist_repo.list_all(search="Edify Audio Lab")
        if not artists:
            sample_artist = await artist_repo.create(
                name="Edify Audio Lab",
                bio="Official sample artist for Edify Music Platform.",
            )
            logger.info("sample_artist_created", name=sample_artist.name)
        else:
            sample_artist = artists[0]

        # 4. Seed Sample Album
        album_repo = AlbumRepository(session)
        albums, _ = await album_repo.list_all(artist_id=sample_artist.id)
        if not albums:
            sample_album = await album_repo.create(
                title="Acoustic Horizons",
                artist_id=sample_artist.id,
                release_year=2026,
            )
            logger.info("sample_album_created", title=sample_album.title)
        else:
            sample_album = albums[0]

        # 5. Seed Sample Song
        song_repo = SongRepository(session)
        songs, _ = await song_repo.list_all(artist_id=sample_artist.id)
        if not songs:
            song_id = uuid.uuid4()
            sample_file_path = storage.music_dir / f"{song_id}.mp3"

            naruto_mp3 = Path(__file__).parent / "Naruto Theme Song.mp3"
            if naruto_mp3.exists():
                audio_bytes = naruto_mp3.read_bytes()
                song_title = "Naruto Theme Song"
                orig_filename = "Naruto Theme Song.mp3"
            else:
                audio_bytes = b"\xff\xfb\x90\xc4\x00\x00\x00\x00" * 400
                song_title = "Horizon Waves"
                orig_filename = "horizon_waves.mp3"

            with open(sample_file_path, "wb") as f:
                f.write(audio_bytes)

            rel_path = sample_file_path.relative_to(storage.base_path).as_posix()

            sample_song = await song_repo.create(
                title=song_title,
                artist_id=sample_artist.id,
                album_id=sample_album.id,
                genre_id=seeded_genres[0].id if seeded_genres else None,
                duration_seconds=180,
                track_number=1,
                file_path=rel_path,
                original_filename=orig_filename,
                mime_type="audio/mpeg",
                file_size_bytes=len(audio_bytes),
            )
            await session.commit()

            # Create default audio variants (64k, 128k, 256k)
            var_dir = storage.variants_dir / str(sample_song.id)
            var_dir.mkdir(parents=True, exist_ok=True)

            bitrates = {"64k": 64000, "128k": 128000, "256k": 256000}
            for quality, bitrate in bitrates.items():
                var_file = var_dir / f"{quality}.mp3"
                with open(var_file, "wb") as f:
                    f.write(audio_bytes)
                rel_var_path = var_file.relative_to(storage.base_path).as_posix()

                await song_repo.create_variant(
                    song_id=sample_song.id,
                    quality=quality,
                    file_path=rel_var_path,
                    bitrate=bitrate,
                    codec="mp3",
                    file_size_bytes=len(audio_bytes),
                    status="ready",
                )
            await session.commit()
            logger.info("sample_song_created", title=sample_song.title)


        logger.info("seeding_completed_successfully")


if __name__ == "__main__":
    asyncio.run(seed_data())
