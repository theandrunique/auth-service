import pytest
from httpx import AsyncClient

from src.database import db_helper
from src.main import app
from src.models import Base

TEST_USER_USERNAME = "johndoe"
TEST_USER_PASSWORD = "INrf3fs@"
TEST_USER_EMAIL = "johndoe@example.com"


@pytest.fixture(autouse=True, scope="session")
async def prepare_test_database(async_client):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await async_client.post(
            "/auth/register/",
            json={
                "username": TEST_USER_USERNAME,
                "password": TEST_USER_PASSWORD,
                "email": TEST_USER_EMAIL,
            },
        )
    yield
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def authorized_header(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    token = response.json()["token"]
    return f"Bearer {token}"
