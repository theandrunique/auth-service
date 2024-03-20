from datetime import timedelta

import pytest
from conftest import client

from src.auth.email_utils import EmailTokenType, generate_email_token

TEST_USER_USERNAME = "emails_test_user"
TEST_USER_PASSWORD = "INrf3fs@"
TEST_USER_SECOND_PASSWORD = "87P(WDasjj903241237@$%)"
TEST_USER_EMAIL = "emails_test_user@example.com"


@pytest.fixture(scope="function")
async def mock_emails(mocker):
    mock_SMTP = mocker.MagicMock()
    mocker.patch("src.auth.email_utils.smtplib.SMTP_SSL", new=mock_SMTP)
    return mock_SMTP


def authorize_test_user():
    response = client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 200, response.json()
    return response.json()["token"]


def test_register_user():
    response = client.post(
        "/auth/register/",
        json={
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
            "email": TEST_USER_EMAIL,
        },
    )
    assert response.status_code == 201, response.json()


def test_verify_email(mock_emails):
    response = client.put(
        "/auth/verify/",
        json={"email": TEST_USER_EMAIL},
        headers={"Authorization": f"Bearer {authorize_test_user()}"},
    )
    assert response.status_code == 204, response.json()

    assert mock_emails.called

    verification_token = generate_email_token(
        email=TEST_USER_EMAIL,
        type=EmailTokenType.VERIFY_EMAIL,
        expires_delta=timedelta(hours=1),
    )
    response = client.post(
        "/auth/verify/",
        json={"token": verification_token},
    )
    assert response.status_code == 204, response.json()


def test_reset_password(mock_emails):
    response = client.post(
        "/auth/forgot/",
        json={"email": TEST_USER_EMAIL},
    )
    assert response.status_code == 204, response.json()

    reset_password_token = generate_email_token(
        email=TEST_USER_EMAIL,
        type=EmailTokenType.RECOVERY_PASSWORD,
        expires_delta=timedelta(hours=1),
    )
    response = client.post(
        "/auth/reset/",
        json={"token": reset_password_token, "password": TEST_USER_SECOND_PASSWORD},
    )
    assert response.status_code == 200, response.json()


def test_new_password():
    response = client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 403, response.json()

    response = client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_SECOND_PASSWORD,
        }
    )
    assert response.status_code == 200, response.json()
