from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.apps.dto import OAuth2AppInfoDTO
from src.oauth2_sessions.service import IOAuthSessionsService
from src.schemas import AppScopes, Scope
from src.services.jwe import JWE
from src.services.jwt import JWT

from .config import settings
from .exceptions import (
    InvalidClientCredentials,
    InvalidRefreshToken,
)


class IOAuthService(ABC):
    @abstractmethod
    def validate_scopes(self, scopes: list[str], req_scopes: list[str]) -> bool: ...

    @abstractmethod
    def get_app_scopes(self) -> list[Scope]: ...

    @abstractmethod
    def create_access_token(self, user_id: UUID, scopes: list[str], client_id: str) -> str: ...

    @abstractmethod
    def create_refresh_token(self, token_id: UUID) -> str: ...

    @abstractmethod
    async def validate_refresh_token(self, refresh_token: str | None): ...

    @abstractmethod
    def validate_client_credentials(
        self, app: OAuth2AppInfoDTO, username: str | None, password: str | None
    ) -> None: ...


@dataclass
class OAuthService:
    sessions_service: IOAuthSessionsService
    scopes: AppScopes
    jwt: JWT
    jwe: JWE

    def validate_scopes(self, scopes: list[str], req_scopes: list[str]) -> bool:
        for scope in req_scopes:
            if scope not in scopes:
                return False
        return True

    def get_app_scopes(self) -> list[Scope]:
        return self.scopes.root

    def create_access_token(self, user_id: UUID, scopes: list[str], client_id: str) -> str:
        return self.jwt.encode(
            payload={
                "sub": user_id,
                "scope": ", ".join(scopes),
                "aud": client_id,
                "exp": datetime.now(UTC) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS),
            }
        )

    def create_refresh_token(self, token_id: UUID) -> str:
        return self.jwe.encode(token_id.bytes)

    async def validate_refresh_token(self, refresh_token: str | None):
        if not refresh_token:
            raise InvalidRefreshToken

        jwe = self.jwe.decode(refresh_token)
        if not jwe:
            raise InvalidRefreshToken
        try:
            token_id = UUID(bytes=jwe)
        except ValueError:
            raise InvalidRefreshToken

        session = await self.sessions_service.get_by_token_id(token_id)
        if not session:
            raise InvalidRefreshToken
        return session

    def validate_client_credentials(self, app: OAuth2AppInfoDTO, username: str | None, password: str | None) -> None:
        try:
            client_id = UUID(username)
            client_secret = UUID(password)
        except Exception:
            raise InvalidClientCredentials

        if app.client_id != client_id:
            raise InvalidClientCredentials
        elif app.client_secret != client_secret:
            raise InvalidClientCredentials
