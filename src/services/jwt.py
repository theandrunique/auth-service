import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import jwt

from .base.jwt import JWT


class UUIDEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return o.hex
        return super().default(o)


@dataclass(kw_only=True)
class ImplJWT(JWT):
    private_key_pem: str
    public_key_pem: str
    public_key_id: str
    issuer: str
    audience: str
    algorithm: str

    def encode(self, payload: dict[str, Any]) -> str:
        payload["iss"] = self.issuer

        encoded = jwt.encode(
            payload=payload,
            key=self.private_key_pem,
            algorithm=self.algorithm,
            json_encoder=UUIDEncoder,
            headers={
                "kid": self.public_key_id,
            },
        )
        return encoded

    def decode(self, token: str) -> dict[str, Any] | None:
        try:
            return jwt.decode(
                jwt=token,
                key=self.public_key_pem,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
            )
        except jwt.InvalidTokenError:
            return None
