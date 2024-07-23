from uuid import uuid4

import jwcrypto
import jwcrypto.jwk
import pytest

from src.schemas import AuthoritativeApp
from src.services.authoritative_apps import AuthoritativeAppsService

AUTHORITATIVE_APP_CLIENT_ID = uuid4()
AUTHORITATIVE_APP_CLIENT_SECRET = uuid4()

PRIVATE_KEY = jwcrypto.jwk.JWK.generate(kty="RSA", size=2048)
PUBLIC_KEY = jwcrypto.jwk.JWK.from_pem(PRIVATE_KEY.export_to_pem())


@pytest.fixture
def authoritative_apps_service() -> AuthoritativeAppsService:
    app = AuthoritativeApp(
        client_id=AUTHORITATIVE_APP_CLIENT_ID,
        client_secret=AUTHORITATIVE_APP_CLIENT_SECRET,
        redirect_uris=["http://localhost:3000/callback"],
        scopes=["read", "write"],
    )
    return AuthoritativeAppsService(
        apps={
            AUTHORITATIVE_APP_CLIENT_ID: app,
        }
    )
