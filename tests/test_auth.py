import jwt
import pytest
from conftest import client, db_helper, settings

from src.auth.crud import get_refresh_token_from_db_by_id, get_user_from_db_by_username


def test_register():
    response = client.post(
        "/register/",
        json={
            "username": "johndoe",
            "password": "12345",
        },
    )

    assert response.status_code == 201


def test_register_name_exists_error():
    response = client.post(
        "/register/",
        json={
            "username": "johndoe",
            "password": "12345",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "User with this username already exists"}


def test_get_token():
    response = client.post(
        "/token/",
        data={
            "username": "johndoe",
            "password": "12345",
        },
    )
    assert response.status_code == 200, response.json()

    json_response = response.json()

    assert "access_token" in json_response
    assert "refresh_token" in json_response
    assert "expires_in" in json_response
    assert "token_type" in json_response


def test_refresh_token(jwt_tokens):
    access_token, refresh_token = jwt_tokens

    response = client.get(
        "/refresh-token/",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 200

    json_response = response.json()

    assert "access_token" in json_response
    assert "refresh_token" in json_response

    new_access_token = json_response["access_token"]
    new_refresh_token = json_response["refresh_token"]

    assert new_access_token != access_token
    assert new_refresh_token != refresh_token

    try:
        _ = jwt.decode(
            new_access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.PyJWTError as e:
        raise AssertionError("New access token invalid") from e

    try:
        _ = jwt.decode(
            new_refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.PyJWTError as e:
        raise AssertionError("New refresh token invalid") from e

    response = client.get(
        "/refresh-token/",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 400, response.json()


@pytest.mark.asyncio
async def test_get_me(jwt_tokens):
    access_token, _ = jwt_tokens

    response = client.get(
        "/me/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    json_response = response.json()

    assert "id" in json_response
    assert "username" in json_response

    async with db_helper.session_factory() as session:
        user = await get_user_from_db_by_username(username="johndoe", session=session)

        assert json_response["id"] == user.id
        assert json_response["username"] == user.username

@pytest.mark.asyncio
async def test_revoke_token(jwt_tokens):
    _, refresh_token = jwt_tokens

    response = client.delete(
        "/revoke-token/",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 200, response.json()

    payload = jwt.decode(
        refresh_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    async with db_helper.session_factory() as session:
        prev_token = await get_refresh_token_from_db_by_id(
            token_id=payload["token_id"],
            session=session,
        )
        assert prev_token is None
