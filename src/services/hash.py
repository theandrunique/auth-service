from abc import ABC, abstractmethod

import bcrypt


class Hash(ABC):
    @abstractmethod
    def create(self, value: str | bytes) -> bytes: ...

    @abstractmethod
    def check(self, value: str | bytes, hashed_value: bytes) -> bool: ...


class ImplHash(Hash):
    def create(self, value: str | bytes) -> bytes:
        if isinstance(value, str):
            value = value.encode()
        elif not isinstance(value, bytes):
            raise ValueError("Value must be either str or bytes.")

        return bcrypt.hashpw(password=value, salt=bcrypt.gensalt())

    def check(self, value: str | bytes, hashed_value: bytes) -> bool:
        if isinstance(value, str):
            value = value.encode()
        elif not isinstance(value, bytes):
            raise ValueError("Value must be either str or bytes.")

        return bcrypt.checkpw(password=value, hashed_password=hashed_value)
