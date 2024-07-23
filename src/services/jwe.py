from abc import ABC, abstractmethod
from dataclasses import dataclass

from jwcrypto import jwe

from src.services.key_manager import KeyManager


class JWE(ABC):
    @abstractmethod
    def encode(self, data: bytes) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> bytes | None: ...


@dataclass
class ImplJWE(JWE):
    key_manager: KeyManager

    def encode(self, data: bytes) -> str:
        key_pair = self.key_manager.get_random_key_pair()
        kid = key_pair.private_key.thumbprint()
        protected_header = {"alg": "RSA-OAEP-256", "enc": "A256CBC-HS512", "typ": "JWE", "kid": kid}
        jwetoken = jwe.JWE(data, recipient=key_pair.public_key, protected=protected_header)
        return jwetoken.serialize(compact=True)

    def decode(self, token: str) -> bytes | None:
        try:
            jwetoken = jwe.JWE()
            jwetoken.deserialize(token)
            kid = jwetoken.jose_header.get("kid")
            if not kid:
                return None

            private_key = self.key_manager.private_keys_by_kid.get(kid)
            if not private_key:
                return None

            jwetoken.decrypt(key=private_key)
            return jwetoken.payload
        except Exception:
            return None
