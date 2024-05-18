from fastapi import APIRouter

from src.config import settings

from .config import key

router = APIRouter(prefix="/.well-known", tags=["well-known"])

jwks = {
    "keys": [
        {
            "kty": key.get("kty"),
            "alg": settings.ALGORITHM,
            "use": "sig",
            "kid": key.thumbprint(),
            "n": key.get("n"),
            "e": key.get("e"),
        }
    ]
}


@router.get("/openid-configuration")
def openid_configuration():
    return {
        "authorization_endpoint": f"{settings.DOMAIN_URL}/oauth/authorize",
        "token_endpoint": f"{settings.DOMAIN_URL}/oauth/token",
        "issuer": settings.DOMAIN_URL,
        "jwks_uri": f"{settings.DOMAIN_URL}/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email"]
    }


@router.get("/jwks.json")
def jwks_endpoint():
    return jwks
