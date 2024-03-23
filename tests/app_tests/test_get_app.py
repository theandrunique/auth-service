from uuid import uuid4

from tests.app_tests.conftest import (
    TEST_APP,
    assert_private_app,
    assert_public_app,
    mock_find_one,
)


async def test_get_public_app(async_client, mock_mongodb):
    mock_mongodb.find_one.side_effect = mock_find_one
    response = await async_client.get(
        f"/app/{TEST_APP['_id']}/",
    )
    assert response.status_code == 200, response.json()
    json_response = response.json()
    assert_public_app(json_response)


async def test_get_private_app(async_client, mock_mongodb, authorized_header):
    mock_mongodb.find_one.side_effect = mock_find_one
    response = await async_client.get(
        f"/app/{TEST_APP['_id']}/",
        headers={"Authorization": authorized_header},
    )
    assert response.status_code == 200, response.json()
    json_response = response.json()
    assert_private_app(json_response)


async def test_app_not_found(async_client, mock_mongodb):
    mock_mongodb.find_one.side_effect = mock_find_one
    response = await async_client.get(
        f"/app/{uuid4()}/",
    )
    assert response.status_code == 404, response.json()
    assert response.json() == {"detail": "App not found"}, response.json()

