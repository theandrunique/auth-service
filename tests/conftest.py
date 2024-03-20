import asyncio  # noqa: I001
from collections.abc import AsyncGenerator
import os

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.database import db_helper
from src.main import app
from src.models import Base


# import models
from src.oauth2.models import OAuth2SessionsInDB  # noqa
from src.auth.models import UserSessionsInDB  # noqa
from src.models import UserInDB  # noqa

if os.path.exists("tests.db"):
    os.remove("tests.db")

SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///tests.db"
db_helper.engine = create_async_engine(url=SQLALCHEMY_DATABASE_URI)
db_helper.session_factory = async_sessionmaker(
    bind=db_helper.engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


TEST_USER_USERNAME = "johndoe"
TEST_USER_PASSWORD = "INrf3fs@"
TEST_USER_EMAIL = "johndoe@example.com"


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # async with db_helper.engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
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
def get_authorization_token() -> str:
    response = client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 200, response.json()
    json_response = response.json()
    return json_response["token"]


client = TestClient(app=app)
