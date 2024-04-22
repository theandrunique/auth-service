from abc import ABC, abstractmethod
from typing import Any

from .object_id import PyObjectId


class Repository(ABC):
    @abstractmethod
    async def add(self, item: Any) -> Any: ...

    @abstractmethod
    async def get_many(self, count: int, offset: int) -> list[Any]: ...

    @abstractmethod
    async def get(self, id: PyObjectId) -> Any: ...

    @abstractmethod
    async def update(self, id: PyObjectId, new_values: dict[str, Any]) -> Any: ...

    @abstractmethod
    async def delete(self, id: PyObjectId) -> int: ...
