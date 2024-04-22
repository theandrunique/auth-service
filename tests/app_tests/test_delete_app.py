async def test_delete_app(async_client, prepare_test_element, authorized_header):
    response = await async_client.delete(
        f"/apps/{prepare_test_element.id}/",
        headers={"Authorization": authorized_header},
    )
    assert response.status_code == 204, response.json()
