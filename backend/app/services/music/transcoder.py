"""
Audio Transcoding Engine
"""
import asyncio
import os
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.song import SongRepository
from app.services.music.storage import StorageService

logger = get_logger(__name__)

QUALITIES = {
    "64k": {"bitrate": 64000, "ffmpeg_b": "64k"},
    "128k": {"bitrate": 128000, "ffmpeg_b": "128k"},
    "256k": {"bitrate": 256000, "ffmpeg_b": "256k"},
}


from app.core.database import AsyncSessionLocal


class TranscoderService:
    def __init__(self, storage_service: StorageService):
        self.storage = storage_service

    def is_ffmpeg_available(self) -> bool:
        return shutil.which("ffmpeg") is not None

    async def transcode_song(self, song_id: uuid.UUID, original_rel_path: str, session: AsyncSession | None = None) -> None:
        if session is None:
            async with AsyncSessionLocal() as fresh_session:
                await self._run_transcoding(song_id, original_rel_path, fresh_session)
        else:
            await self._run_transcoding(song_id, original_rel_path, session)

    async def _run_transcoding(self, song_id: uuid.UUID, original_rel_path: str, session: AsyncSession) -> None:
        song_repo = SongRepository(session)
        original_full_path = self.storage.resolve_path(original_rel_path)

        if not original_full_path.exists():
            logger.error("transcode_failed_original_not_found", song_id=str(song_id), path=str(original_full_path))
            return

        variant_dir = self.storage.variants_dir / str(song_id)
        variant_dir.mkdir(parents=True, exist_ok=True)

        ffmpeg_ok = self.is_ffmpeg_available()

        for quality, info in QUALITIES.items():
            variant_file = variant_dir / f"{quality}.mp3"
            rel_variant_path = str(variant_file.relative_to(self.storage.base_path))

            # Create DB variant record with status 'processing'
            variant = await song_repo.create_variant(
                song_id=song_id,
                quality=quality,
                file_path=rel_variant_path,
                bitrate=info["bitrate"],
                codec="mp3",
                file_size_bytes=0,
                status="processing",
            )
            await session.commit()

            try:
                if ffmpeg_ok:
                    # Run FFmpeg command asynchronously
                    cmd = [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(original_full_path),
                        "-b:a",
                        info["ffmpeg_b"],
                        "-vn",
                        str(variant_file),
                    ]
                    proc = await asyncio.create_subprocess_exec(
                        *cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    await proc.communicate()

                    if proc.returncode == 0 and variant_file.exists():
                        file_size = variant_file.stat().st_size
                        await song_repo.update_variant_status(variant.id, status="ready", file_size_bytes=file_size)
                        await session.commit()
                        logger.info("transcode_variant_success", song_id=str(song_id), quality=quality)
                        continue

                # Fallback if FFmpeg is not installed or returned error: use original file as variant
                shutil.copyfile(original_full_path, variant_file)
                file_size = variant_file.stat().st_size
                await song_repo.update_variant_status(variant.id, status="ready", file_size_bytes=file_size)
                await session.commit()
                logger.info("transcode_variant_fallback_ready", song_id=str(song_id), quality=quality)

            except Exception as exc:
                logger.exception("transcode_variant_error", song_id=str(song_id), quality=quality, error=str(exc))
                await song_repo.update_variant_status(variant.id, status="failed")
                await session.commit()
