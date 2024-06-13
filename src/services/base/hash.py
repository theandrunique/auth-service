from abc import ABC, abstractmethod


class Hash(ABC):
    @abstractmethod
    def create(self, value: str | bytes) -> bytes: ...

    @abstractmethod
    def check(self, value: str | bytes, hashed_value: bytes) -> bool: ...
