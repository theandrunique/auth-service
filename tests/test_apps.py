import copy
import datetime
from uuid import UUID, uuid4

from tests.conftest import TEST_USER_PASSWORD, TEST_USER_USERNAME

TEST_APP_CLIENT_ID = "30219807-9f3f-4da1-bd25-ef0f7abefa1a"
TEST_APP_CLIENT_SECRET = "5d8b84a1-3e18-41d5-8c05-2d77254b21e7"
TEST_APP_NAME = "Test app"
TEST_APP_REDIRECT_URIS = ["http://example.com"]
TEST_APP_SCOPES = ["read", "write"]


TEST_APP = {
    "_id": UUID("6a628054-591c-4618-9edb-008e402b4652"),
    "name": TEST_APP_NAME,
    "client_id": UUID(TEST_APP_CLIENT_ID),
    "client_secret": UUID(TEST_APP_CLIENT_SECRET),
    "redirect_uris": TEST_APP_REDIRECT_URIS,
    "scopes": TEST_APP_SCOPES,
    "creator_id": 1,
    "description": None,
    "website": None,
    "created_at": datetime.datetime.now(),
}


async def mock_find_one(data):
    if data.get("_id") == TEST_APP["_id"]:
        return TEST_APP
    elif data.get("client_id") == TEST_APP["client_id"]:
        return TEST_APP
    else:
        return None


async def mock_find_one_and_update(filter, data, return_document):
    old_app = await mock_find_one(filter)
    new_app_data = old_app.copy()
    new_app_data = copy.deepcopy(old_app)
    new_app_data.update(data["$set"])
    return new_app_data


async def test_create_app(async_client, mock_mongodb_collection_for_apps):
    mock_mongodb_collection_for_apps.insert_one.side_effect = None
    response_token = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    token = response_token.json()["token"]
    response = await async_client.post(
        "/app/",
        json={
            "name": TEST_APP_NAME,
            "redirect_uris": TEST_APP_REDIRECT_URIS,
            "scopes": TEST_APP_SCOPES,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    json_response = response.json()
    assert "id" in json_response
    assert "name" in json_response
    assert "client_id" in json_response
    assert "client_secret" in json_response
    assert "redirect_uris" in json_response
    assert "scopes" in json_response
    assert "creator_id" in json_response
    assert "description" in json_response
    assert "website" in json_response
    assert "created_at" in json_response


async def test_get_public_app(async_client, mock_mongodb_collection_for_apps):
    mock_mongodb_collection_for_apps.find_one.side_effect = mock_find_one
    response = await async_client.get(
        f"/app/{TEST_APP['_id']}/",
    )
    assert response.status_code == 200, response.json()
    json_response = response.json()
    assert "id" in json_response
    assert "name" in json_response
    assert "client_id" in json_response
    assert "client_secret" not in json_response
    assert "redirect_uris" in json_response
    assert "scopes" in json_response
    assert "creator_id" in json_response
    assert "description" in json_response
    assert "website" in json_response
    assert "created_at" in json_response


async def test_get_private_app(async_client, mock_mongodb_collection_for_apps):
    mock_mongodb_collection_for_apps.find_one.side_effect = mock_find_one
    response_token = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    response = await async_client.get(
        f"/app/{TEST_APP['_id']}/",
        headers={"Authorization": f"Bearer {response_token.json()['token']}"},
    )
    assert response.status_code == 200, response.json()
    json_response = response.json()
    assert "id" in json_response
    assert "name" in json_response
    assert "client_id" in json_response
    assert "client_secret" in json_response
    assert "redirect_uris" in json_response
    assert "scopes" in json_response
    assert "creator_id" in json_response
    assert "description" in json_response
    assert "website" in json_response
    assert "created_at" in json_response


async def test_app_not_found(async_client, mock_mongodb_collection_for_apps):
    mock_mongodb_collection_for_apps.find_one.side_effect = mock_find_one
    response = await async_client.get(
        f"/app/{uuid4()}/",
    )
    assert response.status_code == 404, response.json()
    assert response.json() == {"detail": "App not found"}, response.json()


async def test_regenerate_app_secret(async_client, mock_mongodb_collection_for_apps):
    mock_mongodb_collection_for_apps.find_one.side_effect = mock_find_one
    mock_mongodb_collection_for_apps.update_one.side_effect = None
    response_token = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    response = await async_client.put(
        f"/app/{TEST_APP['_id']}/regenerate-client-secret/",
        headers={"Authorization": f"Bearer {response_token.json()['token']}"},
    )
    json_response = response.json()
    assert response.status_code == 200, json_response
    assert json_response["client_secret"] != TEST_APP["client_secret"]
    assert "id" in json_response
    assert "name" in json_response
    assert "client_id" in json_response
    assert "client_secret" in json_response
    assert "redirect_uris" in json_response
    assert "scopes" in json_response
    assert "creator_id" in json_response
    assert "description" in json_response
    assert "website" in json_response
    assert "created_at" in json_response


async def test_update_app(async_client, mock_mongodb_collection_for_apps):
    mock_mongodb_collection_for_apps.find_one.side_effect = mock_find_one
    mock_mongodb_collection_for_apps.find_one_and_update.side_effect = (
        mock_find_one_and_update
    )
    response_token = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    response = await async_client.patch(
        f"/app/{TEST_APP['_id']}/",
        json={
            "name": "Updated name",
            "description": "Updated description",
            "website": "Updated website",
            "redirect_uris": ["http://example.com/updated"],
            "scopes": ["read", "write", "delete"],
        },
        headers={"Authorization": f"Bearer {response_token.json()['token']}"},
    )
    json_response = response.json()
    assert json_response["name"] != TEST_APP["name"]
    assert json_response["description"] != TEST_APP["description"]
    assert json_response["website"] != TEST_APP["website"]
    assert json_response["redirect_uris"] != TEST_APP["redirect_uris"]
    assert json_response["scopes"] != TEST_APP["scopes"]
    assert "id" in json_response
    assert "name" in json_response
    assert "client_id" in json_response
    assert "client_secret" in json_response
    assert "redirect_uris" in json_response
    assert "scopes" in json_response
    assert "creator_id" in json_response
    assert "description" in json_response
    assert "website" in json_response
    assert "created_at" in json_response


async def test_delete_app(async_client, mock_mongodb_collection_for_apps):
    mock_mongodb_collection_for_apps.find_one.side_effect = mock_find_one
    mock_mongodb_collection_for_apps.delete_one.side_effect = None
    response_token = await async_client.post(
        "/auth/login/",
        json={
            "login": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    response = await async_client.delete(
        f"/app/{TEST_APP['_id']}/",
        headers={"Authorization": f"Bearer {response_token.json()['token']}"},
    )
    assert response.status_code == 204, response.json()
