import asyncio  # noqa: I001

import pytest
from unittest.mock import MagicMock  # noqa: F401
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.database import db_helper
from src.main import app
from src.models import Base
from src.auth import email_utils  # noqa


# import models
from src.oauth2.models import OAuth2SessionsInDB  # noqa
from src.auth.models import UserSessionsInDB  # noqa
from src.models import UserInDB  # noqa


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

@pytest.fixture(autouse=True, scope="session")
def prepare_test_user():
    response = client.post(
        "/auth/register/",
        json={
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
            "email": TEST_USER_EMAIL,
        },
    )
    assert response.status_code == 201, response.json()


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://tests") as client:
        yield client


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
