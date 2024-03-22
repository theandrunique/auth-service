import asyncio
from unittest.mock import MagicMock  # noqa: F401

import pytest
from fastapi.testclient import TestClient

from src.auth import email_utils  # noqa
from src.auth.models import UserSessionsInDB  # noqa
from src.database import db_helper
from src.main import app
from src.models import (
    Base,
    UserInDB,  # noqa
)

# import models
from src.oauth2.models import OAuth2SessionsInDB  # noqa

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
    loop = asyncio.get_event_loop()
    if not loop.is_running():
        asyncio.set_event_loop(loop)
    yield loop


@pytest.fixture
def authorization() -> str:
    return get_authorization_token()


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
