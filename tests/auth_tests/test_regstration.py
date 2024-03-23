from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD, TEST_USER_USERNAME


async def test_register_email_taken(async_client, mocker):
    response = await async_client.post(
        "/auth/register/",
        json={
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
            "email": TEST_USER_EMAIL,
        },
    )

    assert response.status_code == 400, response.json()

    assert response.json() == {
        "detail": "User with this username or email already exists"
    }
