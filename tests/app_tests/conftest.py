import datetime
from uuid import UUID

import pytest

from src.apps.schemas import AppInMongo
from tests.app_tests.fake_app_repository import FakeAppsRepository

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


@pytest.fixture(autouse=True)
def patch_mongo(monkeypatch):
    fake_registry = FakeAppsRepository()
    monkeypatch.setattr("src.apps.views.repository", fake_registry)
    monkeypatch.setattr("src.apps.dependencies.repository", fake_registry)
    return fake_registry


@pytest.fixture
async def prepare_test_element(patch_mongo) -> AppInMongo:
    app = AppInMongo(**TEST_APP)
    await patch_mongo.add(app)
    return app


def assert_public_app(json_response):
    expected_keys = [
        "id",
        "name",
        "client_id",
        "redirect_uris",
        "scopes",
        "creator_id",
        "description",
        "website",
        "created_at",
    ]
    for key in expected_keys:
        assert key in json_response

    assert "client_secret" not in json_response


def assert_private_app(json_response):
    expected_keys = [
        "id",
        "name",
        "client_id",
        "client_secret",
        "redirect_uris",
        "scopes",
        "creator_id",
        "description",
        "website",
        "created_at",
    ]
    for key in expected_keys:
        assert key in json_response
