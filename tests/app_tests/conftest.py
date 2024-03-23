import copy
import datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

TEST_APP_CLIENT_ID = "30219807-9f3f-4da1-bd25-ef0f7abefa1a"
TEST_APP_CLIENT_SECRET = "5d8b84a1-3e18-41d5-8c05-2d77254b21e7"
TEST_APP_NAME = "Test app"
TEST_APP_REDIRECT_URIS = ["http://example.com"]
TEST_APP_SCOPES = ["read", "write"]


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


async def mock_find_one_and_update(filter, data, return_document):
    old_app = await mock_find_one(filter)
    new_app_data = old_app.copy()
    new_app_data = copy.deepcopy(old_app)
    new_app_data.update(data["$set"])
    return new_app_data


@pytest.fixture(autouse=True, scope="function")
async def mock_mongodb(mocker):
    mock = AsyncMock()
    mocker.patch("src.apps.views.app_collection", mock)
    return mock

