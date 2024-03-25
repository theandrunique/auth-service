from enum import Enum

from fastapi import APIRouter

from src.apps.exceptions import AppNotFound
from src.apps.schemas import AppInMongo
from src.apps.views import app_collection
from src.auth.dependencies import UserAuthorization
from src.database import DbSession
from src.redis_helper import redis_client

from .exceptions import (
    AuthorizationTypeIsNotSupported,
    InvalidAuthorizationCode,
    InvalidClientSecret,
    NotAllowedScope,
    RedirectUriNotAllowed,
)
from .schemas import (
    OAuth2AuthorizeRequest,
    OAuth2AuthorizeResponse,
    OAuth2CodeExchangeRequest,
)
from .utils import gen_authorization_code, gen_token_pair_and_create_session

router = APIRouter(prefix="", tags=["oauth2"])


class ResponseType(Enum):
    CODE = "code"


@router.post("/authorize/")
async def oauth2_authorize(
    data: OAuth2AuthorizeRequest,
    user: UserAuthorization,
) -> OAuth2AuthorizeResponse:
    found_app = await app_collection.find_one({"client_id": data.client_id})
    if not found_app:
        raise AppNotFound()
    app = AppInMongo(**found_app)

    if data.redirect_uri not in app.redirect_uris:
        raise RedirectUriNotAllowed()

    for scope in data.scopes:
        if scope not in app.scopes:
            raise NotAllowedScope()

    if data.response_type != ResponseType.CODE.value:
        raise AuthorizationTypeIsNotSupported()

    auth_code = gen_authorization_code()

    await redis_client.set(f"auth_code_{app.client_id}_{auth_code}", user.id, ex=60)

    return OAuth2AuthorizeResponse(
        code=auth_code,
        state=data.state,
    )


@router.post("/token/")
async def oauth2_exchange_code(
    data: OAuth2CodeExchangeRequest, session: DbSession
) -> None:
    found_app = await app_collection.find_one({"client_id": data.client_id})
    if not found_app:
        raise AppNotFound()
    app = AppInMongo(**found_app)
    if data.client_secret != app.client_secret:
        raise InvalidClientSecret()

    user_id = await redis_client.get(f"auth_code_{app.client_id}_{data.code}")
    if not user_id:
        raise InvalidAuthorizationCode()

    await redis_client.delete(f"auth_code_{app.client_id}_{data.code}")

    return await gen_token_pair_and_create_session(
        scope=" ".join(app.scopes),
        user_id=user_id,
        app_id=app.id,
        session=session,
    )


@router.post("/refresh/")
async def refresh_token():
    pass


@router.post("/revoke/")
async def revoke_session():
    pass
