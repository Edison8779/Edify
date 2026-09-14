"""
Music Dependencies
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.audit import AuditRepository
from app.services.audit.service import AuditService
from app.services.music.service import MusicService
from app.services.music.storage import StorageService
from app.services.music.transcoder import TranscoderService
from app.services.streaming.service import StreamingService


def get_storage_service() -> StorageService:
    return StorageService()


def get_transcoder_service(
    storage_service: Annotated[StorageService, Depends(get_storage_service)]
) -> TranscoderService:
    return TranscoderService(storage_service)


def get_music_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    transcoder_service: Annotated[TranscoderService, Depends(get_transcoder_service)],
) -> MusicService:
    audit_repo = AuditRepository(session)
    audit_service = AuditService(audit_repo)
    return MusicService(
        session=session,
        audit_service=audit_service,
        storage_service=storage_service,
        transcoder_service=transcoder_service,
    )


def get_streaming_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> StreamingService:
    return StreamingService(session=session, storage_service=storage_service)
