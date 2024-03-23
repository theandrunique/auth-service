from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD, TEST_USER_USERNAME


async def test_login_success_by_username(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 200, response.json()
    assert "token" in response.json()


async def test_login_success_by_email(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 200, response.json()
    assert "token" in response.json()


async def test_login_failed(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": "wrong_password",
        },
    )
    assert response.status_code == 403, response.json()
    assert response.json() == {"detail": "Invalid username or password"}
