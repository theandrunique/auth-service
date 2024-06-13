from abc import ABC, abstractmethod


class JWE(ABC):
    @abstractmethod
    def encode(self, data: bytes) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> bytes | None: ...
