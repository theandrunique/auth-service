from dataclasses import dataclass
from typing import Any

from src.config import settings
from src.oauth2.entities import GrantType, ResponseType
from src.services.key_manager import KeyManager


@dataclass(kw_only=True)
class WellKnownService:
    key_manager: KeyManager

    def get_jwks(self) -> dict[str, Any]:
        keys = []
        for kid, key in self.key_manager.public_keys_by_kid.items():
            keys.append({
                "kty": key.get("kty"),
                "alg": settings.ALGORITHM,
                "use": "sig",
                "kid": kid,
                "n": key.get("n"),
                "e": key.get("e"),
            })
        return {"keys": keys}

    def get_openid_configuration(self) -> dict[str, Any]:
        return {
            "authorization_endpoint": f"{settings.DOMAIN_URL}/oauth/authorize",
            "token_endpoint": f"{settings.DOMAIN_URL}/oauth/token",
            "issuer": settings.DOMAIN_URL,
            "jwks_uri": f"{settings.DOMAIN_URL}/.well-known/jwks.json",
            "response_types_supported": list(ResponseType),
            "grant_types_supported": list(GrantType),
            "id_token_signing_alg_values_supported": ["RS256"],
        }
