import datetime
from uuid import uuid4

from src.emails.schemas import EmailTokenPayload
from src.emails.token_utils import gen_email_token
from src.models import UserInDB
from tests.auth_email_tests.conftest import (
    TEST_RECOVERY_PASS_EMAIL,
    TEST_RECOVERY_PASS_SECOND_PASSWORD,
    TEST_RECOVERY_PASS_USER_USERNAME,
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


async def test_forgot_password(
    async_client, mock_send_email, mock_get_user_from_db_by_email, mock_redis_client
):
    async def get_user_from_db_by_email(email, session):
        return UserInDB(active=True, email_verified=True)

    mock_get_user_from_db_by_email.side_effect = get_user_from_db_by_email
    response = await async_client.post(
        "/auth/forgot/",
        json={
            "email": TEST_RECOVERY_PASS_EMAIL,
        },
    )
    assert response.status_code == 204, response.json()
    assert mock_send_email.called
    assert mock_send_email.return_value.send_message.call_count == 1
    assert mock_redis_client.set.call_count == 1


async def test_reset_password_success(async_client, mock_redis_client_in_dep):
    TEST_JTI = uuid4()

    async def mock_redis_get(key):
        if key == f"reset_password_token_id_{TEST_RECOVERY_PASS_EMAIL}":
            return TEST_JTI.bytes
        return None

    token_for_recovery_password = gen_email_token(
        EmailTokenPayload(
            sub=TEST_RECOVERY_PASS_EMAIL,
            exp=datetime.datetime.now() + datetime.timedelta(hours=1),
            jti=TEST_JTI,
            typ="email",
        )
    )

    mock_redis_client_in_dep.get.side_effect = mock_redis_get
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
