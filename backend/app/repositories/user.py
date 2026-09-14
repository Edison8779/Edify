"""
User Repository
"""
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.auth_identity import AuthIdentity
from app.models.refresh_token import RefreshToken

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email, User.deleted_at.is_(None)))
        return result.scalar_one_or_none()

    async def create_user(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None, avatar_url: Optional[str] = None) -> User:
        user = User(email=email, first_name=first_name, last_name=last_name, avatar_url=avatar_url)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_auth_identity(self, provider: str, provider_id: str) -> Optional[AuthIdentity]:
        result = await self.session.execute(
            select(AuthIdentity).where(AuthIdentity.provider == provider, AuthIdentity.provider_id == provider_id)
        )
        return result.scalar_one_or_none()

    async def create_auth_identity(self, user_id: uuid.UUID, provider: str, provider_id: str, password_hash: Optional[str] = None) -> AuthIdentity:
        auth_identity = AuthIdentity(
            user_id=user_id, 
            provider=provider, 
            provider_id=provider_id,
            password_hash=password_hash
        )
        self.session.add(auth_identity)
        await self.session.flush()
        return auth_identity

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.token == token))
        return result.scalar_one_or_none()

    async def create_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def revoke_refresh_tokens_for_user(self, user_id: uuid.UUID) -> None:
        # Simple implementation, more complex would use an update statement
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False))
        tokens = result.scalars().all()
        for t in tokens:
            t.is_revoked = True
        await self.session.flush()
