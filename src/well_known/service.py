from dataclasses import dataclass
from typing import Any

from jwcrypto import jwk

from src.config import settings
from src.oauth2.schemas import GrantType, ResponseType


@dataclass(kw_only=True)
class WellKnownService:
    private_key: jwk.JWK

    def get_jwks(self) -> dict[str, Any]:
        return {
            "keys": [
                {
                    "kty": self.private_key.get("kty"),
                    "alg": settings.ALGORITHM,
                    "use": "sig",
                    "kid": self.private_key.thumbprint(),
                    "n": self.private_key.get("n"),
                    "e": self.private_key.get("e"),
                }
            ]
        }

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
