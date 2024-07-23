import pytest
from faker import Faker
from httpx import AsyncClient

from src.main import app

TEST_USER_USERNAME = "johndoe"
TEST_USER_PASSWORD = "INrf3fs@"
TEST_USER_EMAIL = "johndoe@example.com"


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def faker():
    return Faker()
