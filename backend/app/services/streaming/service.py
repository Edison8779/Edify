"""
HTTP Range Streaming Service
"""
import os
import uuid
from typing import Optional, Tuple
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.song import SongRepository
from app.services.music.storage import StorageService


class StreamingService:
    def __init__(self, session: AsyncSession, storage_service: StorageService):
        self.session = session
        self.storage = storage_service
        self.song_repo = SongRepository(session)

    async def get_stream_response(
        self, song_id: uuid.UUID, quality: Optional[str], request: Request
    ) -> Response:
        song = await self.song_repo.get_by_id(song_id)
        if not song or not song.is_active:
            raise NotFoundException(code="SONG_NOT_FOUND", message=f"Song {song_id} not found or inactive.")

        # Determine target file path based on quality
        target_rel_path = song.file_path

        if quality and quality.lower() in ("64k", "128k", "256k"):
            variant = await self.song_repo.get_variant_by_quality(song_id, quality.lower())
            if variant and variant.status == "ready" and variant.file_path:
                target_rel_path = variant.file_path

        file_path = self.storage.resolve_path(target_rel_path)
        if not file_path.exists():
            # Fallback to master file if variant file not found
            file_path = self.storage.resolve_path(song.file_path)

        if not file_path.exists():
            raise NotFoundException(code="MEDIA_NOT_FOUND", message="Audio media file not found on disk.")

        file_size = file_path.stat().st_size
        mime_type = song.mime_type or "audio/mpeg"

        # Record play count
        await self.song_repo.increment_play_count(song_id)

        # Parse Range header
        range_header = request.headers.get("range")
        if range_header and range_header.startswith("bytes="):
            start, end = self._parse_range(range_header, file_size)
            content_length = end - start + 1

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": mime_type,
            }

            def iter_file():
                with open(file_path, "rb") as f:
                    f.seek(start)
                    bytes_left = content_length
                    chunk_size = 64 * 1024
                    while bytes_left > 0:
                        read_size = min(chunk_size, bytes_left)
                        data = f.read(read_size)
                        if not data:
                            break
                        bytes_left -= len(data)
                        yield data

            return StreamingResponse(iter_file(), status_code=206, headers=headers)
        else:
            headers = {
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Type": mime_type,
            }

            def iter_full_file():
                with open(file_path, "rb") as f:
                    chunk_size = 64 * 1024
                    while data := f.read(chunk_size):
                        yield data

            return StreamingResponse(iter_full_file(), status_code=200, headers=headers)

    def _parse_range(self, range_header: str, file_size: int) -> Tuple[int, int]:
        bytes_str = range_header.replace("bytes=", "")
        parts = bytes_str.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1

        if start >= file_size:
            start = file_size - 1
        if end >= file_size:
            end = file_size - 1

        return start, end
