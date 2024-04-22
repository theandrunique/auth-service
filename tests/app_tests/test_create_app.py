from tests.app_tests.conftest import (
    assert_private_app,
)


async def test_create_app(async_client, authorized_header):
    TEST_APP_REDIRECT_URIS = ["http://example.com"]
    TEST_APP_SCOPES = ["read", "write"]

    response = await async_client.post(
        "/apps/",
        json={
            "name": "test",
            "redirect_uris": TEST_APP_REDIRECT_URIS,
            "scopes": TEST_APP_SCOPES,
        },
        headers={"Authorization": authorized_header},
    )
    json_response = response.json()
    assert_private_app(json_response)
