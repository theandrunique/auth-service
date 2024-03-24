import json
from typing import Any
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return obj.hex
        return super().default(obj)
