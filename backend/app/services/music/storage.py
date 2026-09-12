"""
File Storage Driver
"""
import os
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO, Tuple
from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    def __init__(self, base_dir: str | None = None):
        if base_dir:
            self.base_path = Path(base_dir)
        else:
            # Fallback to local storage dir if /app/storage does not exist
            default_path = Path(settings.storage_path)
            if not default_path.is_absolute() or not default_path.exists():
                self.base_path = Path(__file__).resolve().parents[3] / "storage"
            else:
                self.base_path = default_path

        self.music_dir = self.base_path / settings.storage_music_dir / "original"
        self.covers_dir = self.base_path / settings.storage_covers_dir
        self.variants_dir = self.base_path / settings.storage_music_dir / "variants"
        self.temp_dir = self.base_path / settings.storage_temp_dir

        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.covers_dir.mkdir(parents=True, exist_ok=True)
        self.variants_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def save_audio_file(self, upload_file: UploadFile, song_id: uuid.UUID) -> Tuple[str, int]:
        ext = Path(upload_file.filename or "song.mp3").suffix or ".mp3"
        filename = f"{song_id}{ext}"
        destination = self.music_dir / filename

        size = 0
        with open(destination, "wb") as buffer:
            while chunk := await upload_file.read(1024 * 1024):
                buffer.write(chunk)
                size += len(chunk)

        # Return relative path for portability
        rel_path = str(destination.relative_to(self.base_path))
        return rel_path, size

    async def save_cover_image(self, upload_file: UploadFile, entity_id: uuid.UUID) -> str:
        ext = Path(upload_file.filename or "cover.png").suffix or ".png"
        filename = f"{entity_id}{ext}"
        destination = self.covers_dir / filename

        with open(destination, "wb") as buffer:
            while chunk := await upload_file.read(1024 * 1024):
                buffer.write(chunk)

        return str(destination.relative_to(self.base_path))

    def resolve_path(self, relative_path: str) -> Path:
        full_path = self.base_path / relative_path
        if not full_path.exists():
            # If path passed was absolute or already relative
            alt_path = Path(relative_path)
            if alt_path.exists():
                return alt_path
        return full_path

    def delete_file(self, relative_path: str) -> None:
        file_path = self.resolve_path(relative_path)
        if file_path.exists() and file_path.is_file():
            try:
                os.remove(file_path)
            except OSError:
                pass
