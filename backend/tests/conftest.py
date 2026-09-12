"""
Pytest Config and Global Fixtures
"""
import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.user import User
from app.core.security import create_access_token, hash_password

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        # Rollback or cleanup after each test
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    from app.models.user import User
    from app.models.auth_identity import AuthIdentity

    user = User(email="testuser@example.com", first_name="Test", last_name="User", is_admin=False)
    db_session.add(user)
    await db_session.flush()

    identity = AuthIdentity(
        user_id=user.id,
        provider="email",
        provider_id="testuser@example.com",
        password_hash=hash_password("Password123!"),
    )
    db_session.add(identity)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> User:
    from app.models.user import User
    from app.models.auth_identity import AuthIdentity

    admin = User(email="admin@example.com", first_name="Admin", last_name="User", is_admin=True)
    db_session.add(admin)
    await db_session.flush()

    identity = AuthIdentity(
        user_id=admin.id,
        provider="email",
        provider_id="admin@example.com",
        password_hash=hash_password("AdminPass123!"),
    )
    db_session.add(identity)
    await db_session.commit()
    return admin


@pytest.fixture
def user_token_headers(test_user: User) -> dict[str, str]:
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token_headers(test_admin: User) -> dict[str, str]:
    token = create_access_token(subject=str(test_admin.id))
    return {"Authorization": f"Bearer {token}"}
