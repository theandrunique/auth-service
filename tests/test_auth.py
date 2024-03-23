from tests.conftest import (
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
)


async def test_register_email_taken(async_client, mocker):
    response = await async_client.post(
        "/auth/register/",
        json={
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
            "email": TEST_USER_EMAIL,
        },
    )

    assert response.status_code == 400, response.json()

    assert response.json() == {
        "detail": "User with this username or email already exists"
    }


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
