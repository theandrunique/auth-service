from conftest import client


def test_create_app(get_authorization_token):
    response = client.post(
        "/app/",
        json={
            "name": "Test app",
            "redirect_uris": ["http://example.com"],
            "scopes": ["read", "write"],
        },
        headers={"Authorization": f"Bearer {get_authorization_token}"},
    )
    app_info = response.json()
    assert response.status_code == 201, response.json()
    # response = client.get(
    #     f"/app/{app_info['id']}",
    #     headers={"Authorization": f"Bearer {get_authorization_token}"},
    # )
    # assert response.status_code == 200
    # json_response = response.json()
    # assert "id" in json_response
    # assert "name" in json_response
    # assert "client_id" in json_response
    # assert "client_secret" in json_response
    # assert "redirect_uris" in json_response
    # assert "scopes" in json_response
    # assert "creator_id" in json_response
    # assert "description" in json_response
    # assert "website" in json_response
    # assert "created_at" in json_response
