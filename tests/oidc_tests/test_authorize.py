from uuid import uuid4

from tests.oidc_tests.conftest import (
    TEST_APP_CLIENT_ID,
    TEST_APP_CLIENT_SECRET,
    TEST_APP_REDIRECT_URIS,
    TEST_APP_SCOPES,
    mock_find_one,
)


async def test_oauth2_authorize_failed(
    async_client, mock_mongodb
):
    mock_mongodb.find_one.side_effect = mock_find_one

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
    async_client, mock_mongodb, authorized_header
):
    mock_mongodb.find_one.side_effect = mock_find_one
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
    async_client, mock_mongodb, authorized_header
):
    mock_mongodb.find_one.side_effect = mock_find_one
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
    async_client, mock_mongodb, authorized_header
):
    mock_mongodb.find_one.side_effect = mock_find_one
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
    async_client, mock_mongodb, authorized_header
):
    mock_mongodb.find_one.side_effect = mock_find_one
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
    mock_mongodb,
    authorized_header,
    mock_redis_client,
):
    mock_mongodb.find_one.side_effect = mock_find_one
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
