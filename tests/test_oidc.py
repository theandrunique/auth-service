import datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from tests.app_tests.conftest import (
    TEST_APP_CLIENT_ID,
    TEST_APP_CLIENT_SECRET,
    TEST_APP_NAME,
    TEST_APP_REDIRECT_URIS,
    TEST_APP_SCOPES,
)

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


async def test_oauth2_authorize_failed(
    async_client, mock_mongodb_collection_for_oauth2
):
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one

    data = {
        "client_id": TEST_APP_CLIENT_ID,
        "redirect_uri": TEST_APP_REDIRECT_URIS[0],
        "scopes": TEST_APP_SCOPES,
        "response_type": "code",
        "state": TEST_APP_CLIENT_SECRET,
    }
    response = await async_client.post("/oauth2/authorize/", json=data)
    json_response = response.json()
    assert response.status_code == 401, json_response
    assert json_response == {"detail": "Not authenticated"}


async def test_oauth2_authorize_failed_not_allowed_uri(
    async_client, mock_mongodb_collection_for_oauth2, authorized_header
):
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one
    data = {
        "client_id": TEST_APP_CLIENT_ID,
        "redirect_uri": "http://notallowed/",
        "scopes": TEST_APP_SCOPES,
        "response_type": "code",
        "state": "test_state",
    }
    response = await async_client.post(
        "/oauth2/authorize/", json=data, headers={"Authorization": authorized_header}
    )
    json_response = response.json()
    assert response.status_code == 400, json_response
    assert json_response == {"detail": "Redirect URI not allowed"}, json_response


async def test_oauth2_authorize_failed_bad_client_id(
    async_client, mock_mongodb_collection_for_oauth2, authorized_header
):
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one
    data = {
        "client_id": uuid4().hex,
        "redirect_uri": TEST_APP_REDIRECT_URIS[0],
        "scopes": TEST_APP_SCOPES,
        "response_type": "code",
        "state": "test_state",
    }
    response = await async_client.post(
        "/oauth2/authorize/", json=data, headers={"Authorization": authorized_header}
    )
    json_response = response.json()
    assert response.status_code == 404, json_response
    assert json_response == {"detail": "App not found"}, json_response


async def test_oauth2_authorize_failed_bad_scopes(
    async_client, mock_mongodb_collection_for_oauth2, authorized_header
):
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one
    data = {
        "client_id": TEST_APP_CLIENT_ID,
        "redirect_uri": TEST_APP_REDIRECT_URIS[0],
        "scopes": ["scope1", "scope2", "scope3"],
        "response_type": "code",
        "state": "test_state",
    }
    response = await async_client.post(
        "/oauth2/authorize/", json=data, headers={"Authorization": authorized_header}
    )
    json_response = response.json()
    assert response.status_code == 400, json_response
    assert json_response == {"detail": "Scope not allowed by app"}, json_response


async def test_oauth2_authorize_failed_bad_response_type(
    async_client, mock_mongodb_collection_for_oauth2, authorized_header
):
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one
    data = {
        "client_id": TEST_APP_CLIENT_ID,
        "redirect_uri": TEST_APP_REDIRECT_URIS[0],
        "scopes": TEST_APP_SCOPES,
        "response_type": "bad_response_type",
        "state": "test_state",
    }
    response = await async_client.post(
        "/oauth2/authorize/", json=data, headers={"Authorization": authorized_header}
    )
    json_response = response.json()
    assert response.status_code == 400, json_response
    assert json_response == {
        "detail": "Authorization type is not supported"
    }, json_response


async def test_oauth2_authorize_success(
    async_client,
    mock_mongodb_collection_for_oauth2,
    authorized_header,
    mock_redis_client,
):
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one
    mock_redis_client.set.side_effect = None
    data = {
        "client_id": TEST_APP_CLIENT_ID,
        "redirect_uri": TEST_APP_REDIRECT_URIS[0],
        "scopes": TEST_APP_SCOPES,
        "response_type": "code",
        "state": "test_state",
    }
    response = await async_client.post(
        "/oauth2/authorize/", json=data, headers={"Authorization": authorized_header}
    )
    json_response = response.json()
    assert response.status_code == 200, json_response
    assert "code" in json_response, json_response
    assert json_response["state"] == "test_state", json_response
    assert mock_redis_client.set.call_count == 1


async def test_oauth2_exchange_code_success(
    async_client, mock_mongodb_collection_for_oauth2, mock_redis_client
):
    mock_redis_client.get.side_effect = mock_redis_get
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one
    data = {
        "client_id": TEST_APP_CLIENT_ID,
        "client_secret": TEST_APP_CLIENT_SECRET,
        "code": TEST_AUTHORIZATION_CODE,
    }
    response = await async_client.post("/oauth2/token/", json=data)
    json_response = response.json()
    assert response.status_code == 200, json_response

    assert "access_token" in json_response
    assert "refresh_token" in json_response
    assert "expires_in" in json_response
    assert json_response["token_type"] == "Bearer"
    assert json_response["scope"] == " ".join(TEST_APP_SCOPES)

    assert mock_redis_client.get.call_count == 1
    assert mock_mongodb_collection_for_oauth2.find_one.call_count == 1


async def test_oauth2_exchange_code_failed_invalid_code(
    async_client, mock_mongodb_collection_for_oauth2, mock_redis_client
):
    mock_redis_client.get.side_effect = mock_redis_get
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one
    data = {
        "client_id": TEST_APP_CLIENT_ID,
        "client_secret": TEST_APP_CLIENT_SECRET,
        "code": "123",
    }
    response = await async_client.post("/oauth2/token/", json=data)
    json_response = response.json()
    assert response.status_code == 400, json_response
    assert json_response == {"detail": "Invalid authorization code"}
    assert mock_redis_client.get.call_count == 1
    assert mock_mongodb_collection_for_oauth2.find_one.call_count == 1


async def test_oauth2_exchange_code_failed_invalid_client_secret(
    async_client, mock_mongodb_collection_for_oauth2, mock_redis_client
):
    mock_redis_client.get.side_effect = mock_redis_get
    mock_mongodb_collection_for_oauth2.find_one.side_effect = mock_find_one
    data = {
        "client_id": TEST_APP_CLIENT_ID,
        "client_secret": uuid4().hex,
        "code": TEST_AUTHORIZATION_CODE,
    }
    response = await async_client.post("/oauth2/token/", json=data)
    json_response = response.json()
    assert response.status_code == 400, json_response
    assert json_response == {"detail": "Invalid client secret"}
    assert mock_redis_client.get.call_count == 0
    assert mock_mongodb_collection_for_oauth2.find_one.call_count == 1
