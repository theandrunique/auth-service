from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, Query

from src.dependencies import Container, Provide, UserAuthorization

from .dependencies import AppAuth
from .exceptions import (
    InvalidRequest,
)
from .schemas import (
    CodeChallengeMethod,
    CodeExchangeResponse,
    GrantType,
    RedirectUriResponse,
    ResponseType,
    WebMessageResponse,
)

router = APIRouter(prefix="", tags=["oauth2"])


@router.post("/authorize", response_model_exclude_none=True)
async def oauth2_authorize(
    user: UserAuthorization,
    response_type: Annotated[ResponseType, Query()],
    client_id: Annotated[UUID, Query()],
    redirect_uri: Annotated[str, Query()],
    scope: Annotated[list[str], Query(default_factory=list)],
    state: Annotated[str | None, Query()] = None,
    code_challenge_method: Annotated[CodeChallengeMethod | None, Query()] = None,
    code_challenge: Annotated[str | None, Query()] = None,
    oauth2_service=Provide(Container.OAuth2Service),
) -> RedirectUriResponse | WebMessageResponse:
    if response_type == ResponseType.code:
        return await oauth2_service.handle_authorize_code(
            client_id=client_id,
            requested_scopes=scope,
            redirect_uri=redirect_uri,
            user=user,
            state=state,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
    elif response_type == ResponseType.token:
        return await oauth2_service.handle_authorize_token(
            client_id=client_id,
            redirect_uri=redirect_uri,
            user=user,
            requested_scopes=scope,
            state=state,
        )
    elif response_type == ResponseType.web_message:
        return await oauth2_service.handle_authorize_web_message(
            client_id=client_id,
            redirect_uri=redirect_uri,
            user=user,
            requested_scopes=scope,
            state=state,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
    raise Exception("Unexpected response type")


@router.post("/token")
async def oauth2_exchange_code(
    app_auth: AppAuth,
    grant_type: Annotated[GrantType, Form()],
    redirect_uri: Annotated[str | None, Form()] = None,
    code: Annotated[str | None, Form()] = None,
    refresh_token: Annotated[str | None, Form()] = None,
    code_verifier: Annotated[str | None, Form()] = None,
    oauth2_service=Provide(Container.OAuth2Service),
) -> CodeExchangeResponse:
    if grant_type == GrantType.authorization_code:
        if code is None:
            raise InvalidRequest("missing code")
        if redirect_uri is None:
            raise InvalidRequest("missing redirect_uri")

        if app_auth:
            return await oauth2_service.handle_code_exchange(code, redirect_uri)
        if code_verifier:
            return await oauth2_service.handle_code_exchange_pkce(
                code, redirect_uri, code_verifier
            )

        raise InvalidRequest("missing code_verifier")
    elif grant_type == GrantType.refresh_token:
        if refresh_token is None:
            raise InvalidRequest("missing refresh_token")

        return await oauth2_service.handle_refresh_token(refresh_token=refresh_token)

    raise Exception("Unsupported grant type")
