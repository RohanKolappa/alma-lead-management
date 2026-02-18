"""Shared test fixtures.

Uses SQLite (async, in-memory) instead of Postgres for test speed — no
external services required.  StaticPool keeps a single DBAPI connection so the
in-memory database persists across requests within a test.  A custom
``gen_random_uuid`` function is registered on the SQLite connection to satisfy
the Lead model's server_default.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.database import Base
from app.main import app
from app.models.lead import Lead  # noqa: F401 — register model metadata

# ---------------------------------------------------------------------------
# Test engine
# ---------------------------------------------------------------------------

test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine.sync_engine, "connect")
def _register_sqlite_functions(dbapi_conn, _connection_record):
    """Register Postgres-compatible helpers so server_defaults work."""
    dbapi_conn.create_function("gen_random_uuid", 0, lambda: uuid.uuid4().hex)


TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
async def _setup_database():
    """Create all tables before each test, drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "attorney@alma.com", "password": "password123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_resume_file() -> tuple[str, bytes, str]:
    return ("resume.pdf", b"%PDF-1.4 test content", "application/pdf")


@pytest.fixture
async def sample_lead(client: AsyncClient, sample_resume_file) -> dict:
    resp = await client.post(
        "/api/v1/leads",
        data={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
        },
        files={"resume": sample_resume_file},
    )
    assert resp.status_code == 201
    return resp.json()
