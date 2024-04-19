from src.emails.utils import (
    send_otp_email,
    send_reset_password_email,
    send_verify_email,
)


async def test_send_verify_email(mock_send_email, mock_redis_client):
    TEST_EMAIL = "test_email@example.com"
    await send_verify_email(TEST_EMAIL, "test")
    assert mock_send_email.called
    assert mock_send_email.call_count == 1
    assert mock_redis_client.set.call_count == 1
    args, _ = mock_redis_client.set.call_args
    assert args[0] == f"verify_email_token_id_{TEST_EMAIL}"


async def test_send_reset_password_email(mock_send_email, mock_redis_client):
    TEST_EMAIL = "test_email@example.com"
    await send_reset_password_email(TEST_EMAIL)
    assert mock_send_email.called
    assert mock_send_email.call_count == 1
    assert mock_redis_client.set.call_count == 1
    args, _ = mock_redis_client.set.call_args
    assert args[0] == f"reset_password_token_id_{TEST_EMAIL}"


async def test_send_otp(mock_send_email, mock_redis_client):
    TEST_EMAIL = "test_email@example.com"
    TEST_USERNAME = "test_username"
    await send_otp_email(TEST_EMAIL, TEST_USERNAME, "test_otp", "test_token")
    assert mock_send_email.called
    assert mock_send_email.call_count == 1
    assert mock_redis_client.set.call_count == 1
    args, _ = mock_redis_client.set.call_args
    assert args[0] == f"otp_{TEST_EMAIL}_test_token"
