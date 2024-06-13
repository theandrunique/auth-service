from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Form, Query

from src.auth.dependencies import UserAuthorization
from src.oauth2.factories import AccessTokenPayloadFactory
from src.oauth2_sessions.dependencies import OAuth2SessionsServiceDep

from .config import settings
from .dependencies import AppAuth, AuthoritativeAppsServiceDep, OAuth2ServiceDep
from .exceptions import (
    InvalidClientId,
    RedirectUriNotAllowed,
)
from .schemas import (
    CodeExchangeResponse,
    GrantType,
    RefreshTokenRequest,
    ResponseType,
)
from .utils import (
    gen_oauth_token,
)

router = APIRouter(prefix="", tags=["oauth2"])


@router.post("/authorize", response_model_exclude_none=True)
async def oauth2_authorize(
    user: UserAuthorization,
    apps_service: AuthoritativeAppsServiceDep,
    oauth2_service: OAuth2ServiceDep,
    client_id: UUID,
    redirect_uri: str,
    response_type: ResponseType,
    scope: list[str] = Query(default=[]),
    state: str | None = None,
) -> Any:
    app = apps_service.get_by_client_id(client_id)
    if not app:
        raise InvalidClientId()

    if redirect_uri not in app.redirect_uris:
        raise RedirectUriNotAllowed()

    if response_type == ResponseType.code:
        code = await oauth2_service.create_request(
            client_id=app.client_id,
            client_secret=app.client_secret,
            user=user,
            requested_scopes=scope,
            redirect_uri=redirect_uri,
        )
        return {
            "code": code,
        }
    elif response_type == ResponseType.token:
        access_payload = AccessTokenPayloadFactory(
            sub=user.id, scopes=scope, aud=str(client_id)
        )
        access_token = gen_oauth_token(access_payload)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            "scope": " ".join(scope),
        }


@router.post("/token")
async def oauth2_exchange_code(
    app: AppAuth,
    code: Annotated[str, Form()],
    redirect_uri: Annotated[str, Form()],
    grant_type: Annotated[GrantType, Form()],
    service: OAuth2SessionsServiceDep,
) -> CodeExchangeResponse: ...


@router.post("/refresh")
async def refresh_token(
    app: AppAuth, data: RefreshTokenRequest, service: OAuth2SessionsServiceDep
) -> CodeExchangeResponse: ...


@router.post("/userinfo")
async def oauth2_userinfo() -> dict:
    return {}
