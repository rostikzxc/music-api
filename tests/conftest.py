from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base
from app.dependencies.db import get_session
from app.main import app

TEST_USERNAME = "test_user"
TEST_PASSWORD = "test-password-123"

t_settings = settings.model_copy(update={"POSTGRES_DB": "music_test", "POSTGRES_HOST": "localhost"})

t_engine = create_async_engine(t_settings.database_url, poolclass=NullPool)

t_SessionLocal = async_sessionmaker(bind=t_engine, expire_on_commit=False)

tables = ", ".join(table.name for table in Base.metadata.sorted_tables)


async def override_get_session() -> AsyncGenerator[AsyncSession]:
    async with t_SessionLocal() as t_session:
        yield t_session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def clean_db() -> AsyncGenerator[None]:
    async with t_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with t_engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/auth/register",
        json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 201, response.text

    return {"username": TEST_USERNAME, "password": TEST_PASSWORD}


@pytest_asyncio.fixture
async def tokens(client: AsyncClient, registered_user: dict[str, str]) -> dict[str, str]:
    response = await client.post(
        "/auth/login",
        data=registered_user,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }
