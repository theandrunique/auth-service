from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from src.auth.email_utils import EmailTokenType, generate_email_token

TEST_EMAIL_USER_USERNAME = "test_email_user"
TEST_EMAIL_USER_PASSWORD = "INrf3fs@"
TEST_EMAIL_USER_SECOND_PASSWORD = "INrf3fs@D*)(AWrefdcas)"
TEST_EMAIL_USER_EMAIL = "test_email@example.com"


@pytest.fixture(autouse=True, scope="session")
async def prepare_test_email_user(async_client):
    await async_client.post(
        "/auth/register/",
        json={
            "username": TEST_EMAIL_USER_USERNAME,
            "password": TEST_EMAIL_USER_PASSWORD,
            "email": TEST_EMAIL_USER_EMAIL,
        },
    )


@pytest.fixture(scope="function")
async def mock_send_email(mocker):
    mock_SMTP = MagicMock()
    mocker.patch("src.auth.email_utils.smtplib.SMTP_SSL", new=mock_SMTP)
    return mock_SMTP


async def test_forgot_password_failed(async_client, mock_send_email):
    response = await async_client.post(
        "/auth/forgot/",
        json={
            "email": TEST_EMAIL_USER_EMAIL,
        },
    )
    assert response.status_code == 400, response.json()
    assert response.json() == {"detail": "Email is not verified"}
    assert mock_send_email.assert_not_called
    assert mock_send_email.return_value.send_message.call_count == 0


async def test_verify_email_failed(async_client):
    response = await async_client.put("/auth/verify/")
    assert response.status_code == 401, response.json()
    assert response.json() == {"detail": "Not authenticated"}


async def test_verify_email_success(async_client, mock_send_email):
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

    verification_token = generate_email_token(
        email=TEST_EMAIL_USER_EMAIL,
        type=EmailTokenType.VERIFY_EMAIL,
        expires_delta=timedelta(hours=1),
    )
    response = await async_client.post(
        "/auth/verify/",
        json={"token": verification_token},
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


async def test_forgot_password(async_client, mock_send_email):
    response = await async_client.post(
        "/auth/forgot/",
        json={
            "email": TEST_EMAIL_USER_EMAIL,
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


async def test_reset_password_failed(async_client):
    verification_token = generate_email_token(
        email=TEST_EMAIL_USER_EMAIL,
        type=EmailTokenType.VERIFY_EMAIL,
        expires_delta=timedelta(hours=1),
    )

    response = await async_client.post(
        "/auth/reset/",
        json={
            "password": TEST_EMAIL_USER_PASSWORD,
            "token": verification_token,
        },
    )
    assert response.status_code == 403, response.json()
    assert response.json() == {"detail": "Invalid token"}


async def test_reset_password_success(async_client):
    verification_token = generate_email_token(
        email=TEST_EMAIL_USER_EMAIL,
        type=EmailTokenType.RECOVERY_PASSWORD,
        expires_delta=timedelta(hours=1),
    )

    response = await async_client.post(
        "/auth/reset/",
        json={
            "password": TEST_EMAIL_USER_SECOND_PASSWORD,
            "token": verification_token,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "active": True,
        "email": "test_email@example.com",
        "id": 2,
        "username": "test_email_user",
    }


async def test_new_password(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_EMAIL_USER_EMAIL,
            "password": TEST_EMAIL_USER_SECOND_PASSWORD,
        },
    )
    assert response.status_code == 200, response.json()
    assert "token" in response.json()


async def test_new_password_failed(async_client):
    response = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_EMAIL_USER_EMAIL,
            "password": TEST_EMAIL_USER_PASSWORD,
        },
    )
    assert response.status_code == 403, response.json()
    assert response.json() == {"detail": "Invalid username or password"}
