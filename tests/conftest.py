import os

os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/online_store_test"

import pytest
from httpx import ASGITransport, AsyncClient

from online_store_api.db.base import Base, engine
from online_store_api.main import app


@pytest.fixture(scope="session", autouse=True)
async def _setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def _truncate_tables():
    yield
    table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        await conn.exec_driver_sql(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
