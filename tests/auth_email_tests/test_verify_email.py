import datetime
from datetime import timedelta
from uuid import uuid4

from src.emails.schemas import EmailTokenPayload
from src.emails.token_utils import gen_email_token
from tests.auth_email_tests.conftest import (
    TEST_EMAIL_USER_EMAIL,
    TEST_EMAIL_USER_PASSWORD,
)


async def test_verify_email_success(
    async_client, mock_send_email, mock_redis_client_in_dep
):
    VERIFY_JTI = uuid4()

    async def mock_redis_get(key):
        if key == f"verify_email_token_id_{TEST_EMAIL_USER_EMAIL}":
            return VERIFY_JTI.bytes
        return None

    mock_redis_client_in_dep.get.side_effect = mock_redis_get
    token_for_verify_email = gen_email_token(
        EmailTokenPayload(
            sub=TEST_EMAIL_USER_EMAIL,
            exp=datetime.datetime.now() + timedelta(hours=1),
            jti=VERIFY_JTI,
            typ="email",
        )
    )
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
