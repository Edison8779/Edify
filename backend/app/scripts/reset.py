"""
Edify Database & Storage Reset Script

Usage:
    python -m app.scripts.reset
"""
import asyncio
import shutil
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger, setup_logging
from app.services.music.storage import StorageService

logger = get_logger(__name__)


async def reset_system() -> None:
    setup_logging()
    logger.info("starting_system_reset_process")

    storage = StorageService()

    async with AsyncSessionLocal() as session:
        # Truncate tables in dependency order
        tables = [
            "song_audio_variants",
            "songs",
            "albums",
            "artists",
            "genres",
            "audit_logs",
            "refresh_tokens",
            "auth_identities",
            "users",
        ]

        for table in tables:
            try:
                await session.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
                logger.info("table_truncated", table=table)
            except Exception as exc:
                logger.warning("truncate_table_failed", table=table, error=str(exc))

        await session.commit()

    # Clean storage directories
    for folder in [storage.music_dir, storage.variants_dir, storage.covers_dir, storage.temp_dir]:
        if folder.exists():
            for item in folder.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

    storage._ensure_dirs()
    logger.info("storage_cleaned_successfully")
    logger.info("reset_completed_successfully")


if __name__ == "__main__":
    asyncio.run(reset_system())
