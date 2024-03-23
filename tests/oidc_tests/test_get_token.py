from uuid import uuid4

from tests.oidc_tests.conftest import (
    TEST_APP_CLIENT_ID,
    TEST_APP_CLIENT_SECRET,
    TEST_APP_SCOPES,
    TEST_AUTHORIZATION_CODE,
    mock_find_one,
    mock_redis_get,
)


async def test_oauth2_exchange_code_success(
    async_client, mock_mongodb, mock_redis_client
):
    mock_redis_client.get.side_effect = mock_redis_get
    mock_mongodb.find_one.side_effect = mock_find_one
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
    assert mock_mongodb.find_one.call_count == 1


async def test_oauth2_exchange_code_failed_invalid_code(
    async_client, mock_mongodb, mock_redis_client
):
    mock_redis_client.get.side_effect = mock_redis_get
    mock_mongodb.find_one.side_effect = mock_find_one
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
    assert mock_mongodb.find_one.call_count == 1


async def test_oauth2_exchange_code_failed_invalid_client_secret(
    async_client, mock_mongodb, mock_redis_client
):
    mock_redis_client.get.side_effect = mock_redis_get
    mock_mongodb.find_one.side_effect = mock_find_one
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
    assert mock_mongodb.find_one.call_count == 1
