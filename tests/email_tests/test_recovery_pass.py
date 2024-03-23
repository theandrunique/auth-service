from tests.email_tests.conftest import (
    TEST_RECOVERY_PASS_EMAIL,
    TEST_RECOVERY_PASS_PASSWORD,
    TEST_RECOVERY_PASS_SECOND_PASSWORD,
    TEST_RECOVERY_PASS_USER_USERNAME,
    verify_email,
)


async def test_forgot_password_failed(async_client, mock_send_email):
    response = await async_client.post(
        "/auth/forgot/",
        json={
            "email": TEST_RECOVERY_PASS_EMAIL,
        },
    )
    assert response.status_code == 400, response.json()
    assert response.json() == {"detail": "Email is not verified"}
    assert mock_send_email.assert_not_called
    assert mock_send_email.return_value.send_message.call_count == 0



async def test_forgot_password(async_client, mock_send_email):
    await verify_email(email=TEST_RECOVERY_PASS_EMAIL, async_client=async_client)
    response = await async_client.post(
        "/auth/forgot/",
        json={
            "email": TEST_RECOVERY_PASS_EMAIL,
        },
    )
    assert response.status_code == 204, response.json()
    assert mock_send_email.called
    assert mock_send_email.return_value.send_message.call_count == 1


async def test_forgot_password_invalid_email(async_client, mock_send_email):
    response = await async_client.post(
        "/auth/forgot/",
        json={
            "email": "test@invalid.com",
        },
    )
    assert response.status_code == 404, response.json()
    assert response.json() == {"detail": "User not found"}
    assert mock_send_email.assert_not_called
    assert mock_send_email.return_value.send_message.call_count == 0


async def test_reset_password_failed(async_client, token_for_verify_email):

    response = await async_client.post(
        "/auth/reset/",
        json={
            "password": TEST_RECOVERY_PASS_PASSWORD,
            "token": token_for_verify_email,
        },
    )
    assert response.status_code == 403, response.json()
    assert response.json() == {"detail": "Invalid token"}


async def test_reset_password_success(async_client, token_for_recovery_password):
    response = await async_client.post(
        "/auth/reset/",
        json={
            "password": TEST_RECOVERY_PASS_SECOND_PASSWORD,
            "token": token_for_recovery_password,
        },
    )
    json_response = response.json()
    assert response.status_code == 200, json_response
    assert json_response["email"] == TEST_RECOVERY_PASS_EMAIL
    assert json_response["username"] == TEST_RECOVERY_PASS_USER_USERNAME


async def test_new_password(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_RECOVERY_PASS_EMAIL,
            "password": TEST_RECOVERY_PASS_SECOND_PASSWORD,
        },
    )
    assert response.status_code == 200, response.json()
    assert "token" in response.json()


async def test_old_password_failed(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_RECOVERY_PASS_EMAIL,
            "password": TEST_RECOVERY_PASS_PASSWORD,
        },
    )
    assert response.status_code == 403, response.json()
    assert response.json() == {"detail": "Invalid username or password"}

