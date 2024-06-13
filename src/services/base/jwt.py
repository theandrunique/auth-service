from abc import ABC, abstractmethod
from typing import Any


class JWT(ABC):
    @abstractmethod
    def encode(self, payload: dict[str, Any]) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> dict[str, Any] | None: ...
