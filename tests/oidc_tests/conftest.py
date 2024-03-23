
import datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

TEST_APP_CLIENT_ID = "30219807-9f3f-4da1-bd25-ef0f7abefa1a"
TEST_APP_CLIENT_SECRET = "5d8b84a1-3e18-41d5-8c05-2d77254b21e7"
TEST_APP_NAME = "Test app"
TEST_APP_REDIRECT_URIS = ["http://example.com"]
TEST_APP_SCOPES = ["read", "write"]

TEST_AUTHORIZATION_CODE = "ud988ff7q3rrfikope8t"
TEST_USER_ID = 1

TEST_APP = {
    "_id": UUID("6a628054-591c-4618-9edb-008e402b4652"),
    "name": TEST_APP_NAME,
    "client_id": UUID(TEST_APP_CLIENT_ID),
    "client_secret": UUID(TEST_APP_CLIENT_SECRET),
    "redirect_uris": TEST_APP_REDIRECT_URIS,
    "scopes": TEST_APP_SCOPES,
    "creator_id": 1,
    "description": None,
    "website": None,
    "created_at": datetime.datetime.now(),
}


async def mock_find_one(data):
    if data.get("_id") == TEST_APP["_id"]:
        return TEST_APP
    elif data.get("client_id") == TEST_APP["client_id"]:
        return TEST_APP
    else:
        return None


@pytest.fixture
async def mock_redis_client(mocker):
    mock = AsyncMock()
    mocker.patch("src.oauth2.views.redis_client", mock)
    yield mock


async def mock_redis_get(key):
    if key == f"auth_code_{TEST_APP_CLIENT_ID}_{TEST_AUTHORIZATION_CODE}":
        return TEST_USER_ID


@pytest.fixture(autouse=True, scope="function")
async def mock_mongodb(mocker):
    mock = AsyncMock()
    mocker.patch("src.oauth2.views.app_collection", mock)
    return mock
