from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Form, Query

from src.dependencies import Container, Provide, UserAuthorization

from .dependencies import AppAuth
from .exceptions import (
    InvalidClientId,
    InvalidRequest,
    RedirectUriNotAllowed,
)
from .schemas import (
    CodeChallengeMethod,
    CodeExchangeResponse,
    GrantType,
    ResponseType,
)

router = APIRouter(prefix="", tags=["oauth2"])


@router.post("/authorize", response_model_exclude_none=True)
async def oauth2_authorize(
    user: UserAuthorization,
    client_id: UUID,
    redirect_uri: str,
    response_type: ResponseType,
    scope: list[str] = Query(default=[]),
    state: str | None = None,
    apps_service=Provide(Container.AppsService),
    oauth2_service=Provide(Container.OAuth2Service),
    code_challenge_method: CodeChallengeMethod | None = Query(default=None),
    code_challenge: str | None = None,
) -> Any:
    app = await apps_service.get_by_client_id(client_id)
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
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
        return {
            "redirect_uri": f"{redirect_uri}?code={code}&state={state}",
            "code": code,
            "state": state,
        }
    elif response_type == ResponseType.token:
        access_token = oauth2_service.create_access_token(
            user_id=user.id, scopes=scope, client_id=str(app.client_id)
        )
        return {
            "redirect_uri": f"{redirect_uri}?access_token={access_token}&token_type=bearer&expires_in=3600&state={state}",
        }

    elif response_type == ResponseType.web_message:
        ...


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
            raise InvalidRequest()
        auth_request = await oauth2_service.validate_code_exchange_request(key=code)
        if not auth_request:
            raise InvalidRequest()

        if auth_request.redirect_uri != redirect_uri:
            raise InvalidRequest()

        if app_auth is None:
            if code_verifier is None:
                raise InvalidRequest()
            return await oauth2_service.handle_authorization_code_with_pkce(
                code_verifier=code_verifier,
                req=auth_request,
            )

        return await oauth2_service.handle_authorization_code(req=auth_request)
    elif grant_type == GrantType.refresh_token:
        if refresh_token is None:
            raise InvalidRequest()
        return await oauth2_service.handle_refresh(token=refresh_token)

    raise Exception("Unsupported grant type")
