"""
Admin Schemas
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AdminDashboardStats(BaseModel):
    total_users: int = 0
    total_songs: int = 0
    total_artists: int = 0
    total_albums: int = 0
    total_genres: int = 0
    total_storage_bytes: int = 0


class UserRoleUpdate(BaseModel):
    is_admin: bool


class UserStatusUpdate(BaseModel):
    is_active: bool


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: uuid.UUID | None = None
    action: str
    target_type: str | None = None
    target_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    status: str
    details: dict | None = None
    created_at: datetime
