"""
Core Auth Service
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.repositories.user import UserRepository

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def generate_tokens_for_user(self, user: User, request: Request | None = None) -> tuple[str, str]:
        access_token = create_access_token(subject=str(user.id))
        refresh_token_str = create_refresh_token(subject=str(user.id))
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
        
        ip_address = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent") if request else None

        rt = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        await self.user_repo.create_refresh_token(rt)
        
        return access_token, refresh_token_str
