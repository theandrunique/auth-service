import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import jwt

from src.services.key_manager import KeyManager

from .base.jwt import JWT


class UUIDEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return o.hex
        return super().default(o)

@dataclass
class ImplJWT(JWT):
    key_manager: KeyManager
    issuer: str
    audience: str
    algorithm: str

    def encode(self, payload: dict[str, Any]) -> str:
        key_pair = self.key_manager.get_random_key_pair()
        kid = key_pair.private_key.thumbprint()
        payload["iss"] = self.issuer
        token = jwt.encode(
            payload=payload,
            key=key_pair.private_key.export_to_pem(private_key=True, password=None), # type: ignore
            json_encoder=UUIDEncoder,
            algorithm=self.algorithm,
            headers={"kid": kid}
        )
        return token

    def decode(self, token: str) -> dict[str, Any] | None:
        unverified_headers = jwt.get_unverified_header(token)
        kid = unverified_headers.get("kid")
        if not kid:
            return None

        public_key = self.key_manager.public_keys_by_kid.get(kid)
        if not public_key:
            return None

        return jwt.decode(token, key=public_key.export_to_pem(), algorithms=[self.algorithm], issuer=self.issuer)
