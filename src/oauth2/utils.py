import base64
import hashlib
import secrets

from src.config import settings


def gen_authorization_code() -> str:
    return secrets.token_urlsafe(settings.AUTHORIZATION_CODE_LENGTH)


def verify_code_verifier(challenge: str, method: str, verifier: str) -> bool:
    if method == "S256":
        verifier_digest = hashlib.sha256(verifier.encode()).digest()
        verifier_base64 = base64.urlsafe_b64encode(verifier_digest).rstrip(b"=").decode("ascii")
        return challenge == verifier_base64
    else:
        return False
