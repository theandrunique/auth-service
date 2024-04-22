from uuid import uuid4

from tests.app_tests.conftest import (
    assert_private_app,
    assert_public_app,
)


async def test_get_public_app(async_client, prepare_test_element):
    response = await async_client.get(
        f"/apps/{prepare_test_element.id}/",
    )
    assert response.status_code == 200, response.json()
    json_response = response.json()
    assert_public_app(json_response)


async def test_get_private_app(async_client, prepare_test_element, authorized_header):
    response = await async_client.get(
        f"/apps/{prepare_test_element.id}/",
        headers={"Authorization": authorized_header},
    )
    assert response.status_code == 200, response.json()
    json_response = response.json()
    assert_private_app(json_response)


async def test_app_not_found(async_client):
    response = await async_client.get(
        f"/apps/{uuid4()}/",
    )
    assert response.status_code == 404, response.json()
    assert response.json() == {"detail": "App not found"}, response.json()
