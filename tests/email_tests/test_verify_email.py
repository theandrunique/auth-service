from tests.email_tests.conftest import TEST_EMAIL_USER_EMAIL, TEST_EMAIL_USER_PASSWORD


async def test_verify_email_failed(async_client):
    response = await async_client.put("/auth/verify/")
    assert response.status_code == 401, response.json()
    assert response.json() == {"detail": "Not authenticated"}


async def test_verify_email_success(
    async_client, mock_send_email, token_for_verify_email
):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_EMAIL_USER_EMAIL,
            "password": TEST_EMAIL_USER_PASSWORD,
        },
    )
    authorization = f"Bearer {response.json()['token']}"
    response = await async_client.put(
        "/auth/verify/", headers={"Authorization": authorization}
    )
    assert response.status_code == 204, response.json()
    assert mock_send_email.called
    assert mock_send_email.return_value.send_message.call_count == 1
    response = await async_client.post(
        "/auth/verify/",
        json={"token": token_for_verify_email},
    )
    assert response.status_code == 204, response.json()


async def test_verify_email_invalid_token(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_EMAIL_USER_EMAIL,
            "password": TEST_EMAIL_USER_PASSWORD,
        },
    )
    response = await async_client.post(
        "/auth/verify/",
        json={"token": response.json()["token"]},
    )
    assert response.status_code == 403, response.json()
    assert response.json() == {"detail": "Invalid token"}
