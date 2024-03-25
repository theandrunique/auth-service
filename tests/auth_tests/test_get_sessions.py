from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD


async def test_get_sessions_failed(async_client):
    response = await async_client.get("/auth/sessions/")
    assert response.status_code == 401, response.json()
    assert response.json() == {"detail": "Not authenticated"}


async def test_get_sessions_success(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )
    authorization = f"Bearer {response.json()['token']}"

    response = await async_client.get(
        "/auth/sessions/", headers={"Authorization": authorization}
    )
    assert response.status_code == 200, response.json()
