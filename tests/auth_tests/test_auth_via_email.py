from unittest.mock import patch

from src.emails.dependencies import get_otp
from src.main import app
from src.models import UserInDB


async def test_send_otp(async_client):
    TEST_EMAIL = "test@example.com"

    async def mock_get_user_from_db_by_email(email, session):
        return UserInDB(username="test", email=email, active=True, email_verified=True)

    with patch(
        "src.auth.views.get_user_from_db_by_email", mock_get_user_from_db_by_email
    ):
        with patch("src.auth.views.send_otp_email") as send_otp_email:
            response = await async_client.put(
                "/auth/otp/",
                json={
                    "email": TEST_EMAIL,
                },
            )
            json_response = response.json()
            assert response.status_code == 200, json_response
            assert "token" in json_response

            assert send_otp_email.call_count == 1
            args, _ = send_otp_email.call_args
            assert args[0] == TEST_EMAIL
            assert args[1] == "test"
            assert args[3] == json_response["token"]


async def test_otp_auth(async_client):
    TEST_EMAIL = "test@example.com"

    async def mock_get_user_from_db_by_email(email, session):
        return UserInDB(
            id=1, username="test", email=email, active=True, email_verified=True
        )

    app.dependency_overrides[get_otp] = lambda: TEST_EMAIL
    with patch(
        "src.auth.views.get_user_from_db_by_email", mock_get_user_from_db_by_email
    ):
        with patch("src.auth.views.create_new_user_session"):
            response = await async_client.post(
                "/auth/otp/",
                json={
                    "email": TEST_EMAIL,
                    "token": "test",
                    "otp": "test",
                },
            )
            json_response = response.json()
            assert response.status_code == 200, json_response
            assert json_response["user_id"] == 1
            assert json_response["token"]
