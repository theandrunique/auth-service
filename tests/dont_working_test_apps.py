from conftest import TEST_USER_PASSWORD, TEST_USER_USERNAME, client


class TestApp:
    def setup_method(self, method):
        response = client.post(
            "/auth/login/",
            json={
                "login": TEST_USER_USERNAME,
                "password": TEST_USER_PASSWORD,
            },
        )
        assert response.status_code == 200, response.json()
        json_response = response.json()
        self.authorization = json_response["token"]
        self.app = self.create_app()


    def create_app(self):
        response = client.post(
            "/app/",
            json={
                "name": "Test app",
                "redirect_uris": ["http://example.com"],
                "scopes": ["read", "write"],
            },
            headers={"Authorization": f"Bearer {self.authorization}"},
        )
        assert response.status_code == 201
        return response.json()


    def test_get_app(self):
        response = client.get(
            f"/app/{self.app['id']}",
            headers={"Authorization": f"Bearer {self.authorization}"},
        )
        assert response.status_code == 200
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


    def test_get_app_public(self):
        response = client.get(
            f"/app/{self.app['id']}",
        )
        assert response.status_code == 200
        json_response = response.json()
        assert "id" in json_response
        assert "name" in json_response
        assert "client_id" not in json_response
        assert "client_secret" not in json_response
        assert "redirect_uris" not in json_response
        assert "scopes" in json_response
        assert "creator_id" in json_response
        assert "description" in json_response
        assert "website" in json_response
        assert "created_at" in json_response

