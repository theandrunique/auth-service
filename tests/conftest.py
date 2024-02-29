import asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings
from src.db_helper import db_helper
from src.main import app
from src.models import Base


settings.DB_URL = "sqlite+aiosqlite:///auth.db"
db_helper.engine = create_async_engine(settings.DB_URL)
db_helper.session_factory = async_sessionmaker(
    bind=db_helper.engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://localhost:8080") as ac:
        yield ac


@pytest.fixture
def jwt_tokens():
    response = client.post("/token/", data={
        "username": "johndoe",
        "password": "12345",
        "scope": ["me"]
    })
    json_response = response.json()
    return json_response["access_token"], json_response["refresh_token"]


client = TestClient(app=app)

