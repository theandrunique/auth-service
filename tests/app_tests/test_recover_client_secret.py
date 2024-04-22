async def test_regenerate_client_secret(
    async_client, prepare_test_element, authorized_header
):
    response = await async_client.put(
        f"/apps/{prepare_test_element.id}/regenerate-client-secret/",
        headers={"Authorization": authorized_header},
    )
    assert response.status_code == 200
    assert response.json()["client_secret"] != prepare_test_element.client_secret
