from tests.app_tests.conftest import (
    TEST_APP,
    assert_private_app,
)


async def test_regenerate_app_secret(
    async_client, prepare_test_element, authorized_header
):
    response = await async_client.put(
        f"/apps/{prepare_test_element.id}/regenerate-client-secret/",
        headers={"Authorization": authorized_header},
    )
    json_response = response.json()
    assert response.status_code == 200, json_response
    assert json_response["client_secret"] != TEST_APP["client_secret"]
    assert_private_app(json_response)


async def test_update_app(async_client, prepare_test_element, authorized_header):
    response = await async_client.patch(
        f"/apps/{prepare_test_element.id}/",
        json={
            "name": "Updated name",
            "description": "Updated description",
            "website": "Updated website",
            "redirect_uris": ["http://example.com/updated"],
            "scopes": ["read", "write", "delete"],
        },
        headers={"Authorization": authorized_header},
    )
    json_response = response.json()
    assert json_response["name"] != TEST_APP["name"]
    assert json_response["description"] != TEST_APP["description"]
    assert json_response["website"] != TEST_APP["website"]
    assert json_response["redirect_uris"] != TEST_APP["redirect_uris"]
    assert json_response["scopes"] != TEST_APP["scopes"]
    assert_private_app(json_response)
