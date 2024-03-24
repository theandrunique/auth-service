from unittest.mock import AsyncMock, MagicMock

import pytest


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
