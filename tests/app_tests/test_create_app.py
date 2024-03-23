from tests.app_tests.conftest import (
    TEST_APP_NAME,
    TEST_APP_REDIRECT_URIS,
    TEST_APP_SCOPES,
)


async def test_create_app(async_client, mock_mongodb, authorized_header):
    mock_mongodb.insert_one.side_effect = None
    response = await async_client.post(
        "/app/",
        json={
            "name": TEST_APP_NAME,
            "redirect_uris": TEST_APP_REDIRECT_URIS,
            "scopes": TEST_APP_SCOPES,
        },
        headers={"Authorization": authorized_header},
    )
    json_response = response.json()
    assert "id" in json_response
    assert "name" in json_response
    assert "client_id" in json_response
    assert "client_secret" in json_response
    assert "redirect_uris" in json_response
    assert "scopes" in json_response
    assert "creator_id" in json_response
    assert "description" in json_response
    assert "website" in json_response
    assert "created_at" in json_response
