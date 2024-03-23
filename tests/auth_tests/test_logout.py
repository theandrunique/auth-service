from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD


async def test_logout_success(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )
    authorization = f"Bearer {response.json()['token']}"

    response = await async_client.delete(
        "/auth/logout/", headers={"Authorization": authorization}
    )
    assert response.status_code == 204, response.json()


async def test_logout_failed(async_client):
    response = await async_client.delete("/auth/logout/")
    assert response.status_code == 401, response.json()
    assert response.json() == {"detail": "Not authenticated"}
