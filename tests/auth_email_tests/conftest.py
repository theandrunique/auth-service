from unittest.mock import AsyncMock, MagicMock

import pytest

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


@pytest.fixture(scope="function")
async def mock_send_email(mocker):
    mock_SMTP = MagicMock()
    mocker.patch("src.emails.utils.smtplib.SMTP_SSL", new=mock_SMTP)
    return mock_SMTP


@pytest.fixture(scope="function")
async def mock_redis_client(mocker):
    mock = AsyncMock()
    mocker.patch("src.emails.main.redis_client", new=mock)
    return mock


@pytest.fixture(scope="function")
async def mock_get_user_from_db_by_email(mocker):
    mock = AsyncMock()
    mocker.patch("src.auth.views.get_user_from_db_by_email", new=mock)
    return mock


@pytest.fixture(scope="function")
async def mock_redis_client_in_dep(mocker):
    mock = AsyncMock()
    mocker.patch("src.emails.dependencies.redis_client", new=mock)
    return mock
