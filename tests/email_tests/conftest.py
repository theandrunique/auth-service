from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from src.auth.email_utils import EmailTokenType, generate_email_token

TEST_EMAIL_USER_USERNAME = "test_email_user"
TEST_EMAIL_USER_PASSWORD = "INrf3fs@"
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


TEST_RECOVERY_PASS_USER_USERNAME = "test_recovery_pass_user"
TEST_RECOVERY_PASS_PASSWORD = "INrf3fs@"
TEST_RECOVERY_PASS_SECOND_PASSWORD = "INrf3fs@D*)(AWrefdcas)"
TEST_RECOVERY_PASS_EMAIL = "test_recovery_pass_user@example.com"



@pytest.fixture(autouse=True, scope="session")
async def prepare_test_recovery_pass_user(async_client):
    await async_client.post(
        "/auth/register/",
        json={
            "username": TEST_RECOVERY_PASS_USER_USERNAME,
            "password": TEST_RECOVERY_PASS_PASSWORD,
            "email": TEST_RECOVERY_PASS_EMAIL,
        },
    )


async def verify_email(email, async_client):
    verification_token = generate_email_token(
        email=email,
        type=EmailTokenType.VERIFY_EMAIL,
        expires_delta=timedelta(hours=1),
    )
    response = await async_client.post(
        "/auth/verify/",
        json={"token": verification_token},
    )
    assert response.status_code == 204, response.json()


@pytest.fixture(scope="function")
async def mock_send_email(mocker):
    mock_SMTP = MagicMock()
    mocker.patch("src.auth.email_utils.smtplib.SMTP_SSL", new=mock_SMTP)
    return mock_SMTP


@pytest.fixture
def token_for_verify_email():
    return generate_email_token(
        email=TEST_EMAIL_USER_EMAIL,
        type=EmailTokenType.VERIFY_EMAIL,
        expires_delta=timedelta(hours=1),
    )


@pytest.fixture
def token_for_recovery_password():
    return generate_email_token(
        email=TEST_RECOVERY_PASS_EMAIL,
        type=EmailTokenType.RECOVERY_PASSWORD,
        expires_delta=timedelta(hours=1),
    )
