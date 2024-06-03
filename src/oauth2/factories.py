from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from src.config import settings as global_settings

from .config import settings


@dataclass
class TokenPayloadFactory:
    sub: UUID

    def dump(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AccessTokenPayloadFactory(TokenPayloadFactory):
    scopes: list[str]
    aud: str
    exp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
        + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    )


@dataclass
class RefreshTokenPayloadFactory(TokenPayloadFactory):
    aud: str = field(default=global_settings.DOMAIN_URL)
    jti: UUID = field(default_factory=lambda: uuid4())
    exp: datetime = field(
        default_factory=lambda: datetime.now()
        + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
    )
