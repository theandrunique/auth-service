from uuid import UUID

from fastapi import APIRouter, Query

from src.apps.dependencies import ExistedAppByClientId
from src.dependencies import UserAuthorization
from src.oauth2_sessions.dependencies import get_oauth2_sessions_service_by_id
from src.oauth2_sessions.schemas import OAuth2SessionCreate
from src.redis import RedisClient

from .config import settings
from .dependencies import AppAuth
from .exceptions import (
    InvalidAuthorizationCode,
    InvalidSession,
    NotAllowedScope,
    RedirectUriNotAllowed,
)
from .schemas import (
    OAuth2AccessTokenPayload,
    OAuth2AuthorizeResponse,
    OAuth2CodeExchangeRequest,
    OAuth2CodeExchangeResponse,
    OAuth2RefreshTokenPayload,
    RefreshTokenRequest,
)
from .utils import (
    create_token_pair,
    gen_authorization_code,
    validate_refresh_token,
)

router = APIRouter(prefix="", tags=["oauth2"])


@router.post("/authorize/", response_model_exclude_none=True)
async def oauth2_authorize(
    user: UserAuthorization,
    app: ExistedAppByClientId,
    redis: RedisClient,
    redirect_uri: str,
    scopes: list[str],
    response_type: str = Query(pattern="code"),
    state: str | None = None,
) -> OAuth2AuthorizeResponse:
    if redirect_uri not in app.redirect_uris:
        raise RedirectUriNotAllowed()

    disallowed_scopes = [scope for scope in scopes if scope not in app.scopes]
    if disallowed_scopes:
        raise NotAllowedScope(disallowed_scopes)

    auth_code = gen_authorization_code()

    await redis.set(
        f"auth_code_{redirect_uri}_{app.client_id}_{auth_code}",
        user.id.hex,
        ex=settings.AUTHORIZATION_CODE_EXPIRE_SECONDS,
    )

    return OAuth2AuthorizeResponse(
        code=auth_code,
        state=state,
    )


@router.post("/token/")
async def oauth2_exchange_code(
    app: AppAuth,
    data: OAuth2CodeExchangeRequest,
    redis: RedisClient,
) -> OAuth2CodeExchangeResponse:
    user_id = await redis.get(
        f"auth_code_{data.redirect_uri}_{app.client_id}_{data.code}"
    )
    if not user_id:
        raise InvalidAuthorizationCode()

    await redis.delete(f"auth_code_{data.redirect_uri}_{app.client_id}_{data.code}")

    refresh_payload = OAuth2RefreshTokenPayload(sub=UUID(user_id))
    access_token, refresh_token = create_token_pair(
        payload=OAuth2AccessTokenPayload(sub=UUID(user_id), scopes=app.scopes),
        refresh_payload=refresh_payload,
    )
    service = get_oauth2_sessions_service_by_id(user_id)

    await service.add(
        OAuth2SessionCreate(
            refresh_token_id=refresh_payload.jti,
            app_id=app.id,
            scopes=app.scopes,
        )
    )

    return OAuth2CodeExchangeResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        scopes=app.scopes,
    )


@router.post("/refresh/")
async def refresh_token(
    app: AppAuth,
    data: RefreshTokenRequest,
) -> OAuth2CodeExchangeResponse:
    payload = validate_refresh_token(data.refresh_token)
    if payload is None:
        raise InvalidSession()

    service = get_oauth2_sessions_service_by_id(payload.sub)
    session = await service.get_by_jti(payload.jti)
    if not session:
        raise InvalidSession()

    refresh_payload = OAuth2RefreshTokenPayload(sub=payload.sub)
    access_token, refresh_token = create_token_pair(
        payload=OAuth2AccessTokenPayload(sub=payload.sub, scopes=session.scopes),
        refresh_payload=refresh_payload,
    )
    await service.update_jti(id=session.id, new_jti=refresh_payload.jti)

    return OAuth2CodeExchangeResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        scopes=app.scopes,
    )
