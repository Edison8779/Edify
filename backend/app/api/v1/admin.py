"""
Admin Router
"""
import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_admin
from app.models.album import Album
from app.models.artist import Artist
from app.models.audit_log import AuditLog
from app.models.genre import Genre
from app.models.song import Song
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.repositories.user import UserRepository
from app.schemas.admin import AdminDashboardStats, AuditLogResponse, UserRoleUpdate, UserStatusUpdate
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=DataResponse[AdminDashboardStats])
async def get_admin_stats(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> DataResponse[AdminDashboardStats]:
    user_count = (await session.execute(select(func.count(User.id)).where(User.deleted_at.is_(None)))).scalar() or 0
    song_count = (await session.execute(select(func.count(Song.id)).where(Song.deleted_at.is_(None)))).scalar() or 0
    artist_count = (await session.execute(select(func.count(Artist.id)).where(Artist.deleted_at.is_(None)))).scalar() or 0
    album_count = (await session.execute(select(func.count(Album.id)).where(Album.deleted_at.is_(None)))).scalar() or 0
    genre_count = (await session.execute(select(func.count(Genre.id)))).scalar() or 0

    storage_bytes = (await session.execute(select(func.sum(Song.file_size_bytes)).where(Song.deleted_at.is_(None)))).scalar() or 0

    stats = AdminDashboardStats(
        total_users=user_count,
        total_songs=song_count,
        total_artists=artist_count,
        total_albums=album_count,
        total_genres=genre_count,
        total_storage_bytes=storage_bytes,
    )
    return DataResponse(data=stats)


@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_admin)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> PaginatedResponse[UserResponse]:
    query = select(User).where(User.deleted_at.is_(None))
    count_res = await session.execute(select(func.count()).select_from(query.subquery()))
    total = count_res.scalar() or 0

    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    res = await session.execute(query)
    users = res.scalars().all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        data=[UserResponse.model_validate(u) for u in users],
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
    )


@router.patch("/users/{user_id}/role", response_model=DataResponse[UserResponse])
async def update_user_role(
    user_id: uuid.UUID,
    data: UserRoleUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> DataResponse[UserResponse]:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(code="USER_NOT_FOUND", message="User not found")

    user.is_admin = data.is_admin
    session.add(user)
    await session.commit()
    return DataResponse(data=UserResponse.model_validate(user))


@router.patch("/users/{user_id}/status", response_model=DataResponse[UserResponse])
async def update_user_status(
    user_id: uuid.UUID,
    data: UserStatusUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_admin)],
) -> DataResponse[UserResponse]:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("User not found")

    user.is_active = data.is_active
    session.add(user)
    await session.commit()
    return DataResponse(data=UserResponse.model_validate(user))


@router.get("/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_admin)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> PaginatedResponse[AuditLogResponse]:
    query = select(AuditLog)
    count_res = await session.execute(select(func.count()).select_from(query.subquery()))
    total = count_res.scalar() or 0

    query = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    res = await session.execute(query)
    logs = res.scalars().all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        data=[AuditLogResponse.model_validate(l) for l in logs],
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
    )
