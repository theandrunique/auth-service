from uuid import UUID

from jwcrypto import jwe

from src.well_known.config import private_key, public_key


def create_session_token(session_id: UUID) -> str:
    protected_header = {
        "alg": "RSA-OAEP-256",
        "enc": "A256CBC-HS512",
        "typ": "JWE",
        "kid": private_key.thumbprint(),
    }

    jwetoken = jwe.JWE(
        session_id.bytes, recipient=public_key, protected=protected_header
    )
    return jwetoken.serialize(compact=True)


def verify_session_token(token: str) -> UUID | None:
    try:
        jwetoken = jwe.JWE()
        jwetoken.deserialize(token, key=private_key)
        return UUID(bytes=jwetoken.payload)
    except Exception as e:
        print(e)
        return None
