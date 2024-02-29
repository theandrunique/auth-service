import jwt
import pytest
from conftest import client, settings, db_helper
from src.auth.crud import get_user_from_db_by_username


def test_register():
    response = client.post("/register/", json={
        "username": "johndoe",
        "password": "12345",
    })
    
    assert response.status_code == 201
    

def test_register_name_exists_error():
    response = client.post("/register/", json={
        "username": "johndoe",
        "password": "12345",
    })
    
    assert response.status_code == 400
    assert response.json() == {"detail": "User with this username already exists"}
    
    
def test_get_token():
    response = client.post("/token/", data={
        "username": "johndoe",
        "password": "12345",
    })
    assert response.status_code == 200, response.json()
    
    json_response = response.json()
    
    assert "access_token" in json_response
    assert "refresh_token" in json_response
    


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
    assert new_refresh_token !=  refresh_token

    try:
        _ = jwt.decode(new_access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        assert False, "New access token invalid"

    try:
        _ = jwt.decode(new_refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        assert False, "New refresh token invalid"

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
    assert  "username" in json_response
    
    async with db_helper.session_factory() as session:
        user = await get_user_from_db_by_username(username="johndoe", session=session)
    
        assert json_response["id"] == user.id
        assert json_response["username"] == user.username
