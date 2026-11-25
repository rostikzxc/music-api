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
