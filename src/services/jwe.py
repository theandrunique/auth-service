from dataclasses import dataclass

from jwcrypto import jwe, jwk

from .base.jwe import JWE


@dataclass(kw_only=True)
class ImplJWE(JWE):
    public_key: jwk.JWK
    private_key: jwk.JWK

    def encode(self, data: bytes) -> str:
        protected_header = {
            "alg": "RSA-OAEP-256",
            "enc": "A256CBC-HS512",
            "typ": "JWE",
            "kid": self.private_key.thumbprint(),
        }

        jwetoken = jwe.JWE(data, recipient=self.public_key, protected=protected_header)
        return jwetoken.serialize(compact=True)

    def decode(self, token: str) -> bytes | None:
        try:
            jwetoken = jwe.JWE()
            jwetoken.deserialize(token, key=self.private_key)
            return jwetoken.payload
        except Exception:
            return None
