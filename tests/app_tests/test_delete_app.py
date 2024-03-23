from tests.app_tests.conftest import TEST_APP, mock_find_one


async def test_delete_app(async_client, mock_mongodb, authorized_header):
    mock_mongodb.find_one.side_effect = mock_find_one
    mock_mongodb.delete_one.side_effect = None
    response = await async_client.delete(
        f"/app/{TEST_APP['_id']}/",
        headers={"Authorization": authorized_header},
    )
    assert response.status_code == 204, response.json()
