from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Body, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

from src.dependencies import Provide
from src.oauth2.entities import CodeChallengeMethod, GrantType, ResponseMode, ResponseType
from src.oauth2.responses import RedirectUri, WebMessage
from src.oauth2.use_cases import (
    GetAppScopesUseCase,
    OAuthAuthorizeCommand,
    OAuthAuthorizeUseCase,
    OAuthRequestCommand,
    OAuthRequestUseCase,
    OAuthTokenCommand,
    OAuthTokenUseCase,
)
from src.schemas import Scope
from src.sessions.dependencies import SessionCookie

from .dependencies import AppAuth
from .schemas import CodeExchangeResponseSchema, OAuthRequestValidateResponseSchema

router = APIRouter(prefix="/oauth", tags=["oauth2"])


@router.post("/request")
async def oauth_request(
    session_token: SessionCookie,
    response_type: Annotated[ResponseType, Body()],
    client_id: Annotated[UUID, Body()],
    redirect_uri: Annotated[str, Body()],
    scope: Annotated[str, Body()],
    state: Annotated[str | None, Body()] = None,
    response_mode: Annotated[ResponseMode, Body()] = ResponseMode.query,
    code_challenge_method: Annotated[CodeChallengeMethod | None, Body()] = None,
    code_challenge: Annotated[str | None, Body()] = None,
    use_case=Provide(OAuthRequestUseCase),
):
    scopes = scope.split(",")

    res = await use_case.execute(
        OAuthRequestCommand(
            session_token=session_token.token if session_token else "",
            response_type=response_type,
            client_id=client_id,
            redirect_uri=redirect_uri,
            response_mode=response_mode,
            scope=scopes,
            state=state,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
    )
    return OAuthRequestValidateResponseSchema(
        scopes=res.requested_scopes,
    )


@router.post("/authorize/accept")
async def oauth2_authorize(
    session_token: SessionCookie,
    response_type: Annotated[ResponseType, Form()],
    client_id: Annotated[UUID, Form()],
    redirect_uri: Annotated[str, Form()],
    scope: Annotated[str, Body()],
    state: Annotated[str | None, Form()] = None,
    response_mode: Annotated[ResponseMode, Body()] = ResponseMode.query,
    code_challenge_method: Annotated[CodeChallengeMethod | None, Form()] = None,
    code_challenge: Annotated[str | None, Form()] = None,
    use_case=Provide(OAuthAuthorizeUseCase),
) -> Any:
    scopes = scope.split(",")
    res = await use_case.execute(
        OAuthAuthorizeCommand(
            session_token=session_token.token if session_token else "",
            response_type=response_type,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scopes,
            response_mode=response_mode,
            state=state,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
    )
    if isinstance(res, RedirectUri):
        return RedirectResponse(url=res.build(), status_code=status.HTTP_200_OK)
    elif isinstance(res, WebMessage):
        response = res.build()
        return HTMLResponse(
            content=response.content,
            headers=response.headers,
        )

    raise NotImplementedError


@router.post("/token", response_model=CodeExchangeResponseSchema)
async def oauth2_exchange_code(
    app_auth: AppAuth,
    grant_type: Annotated[GrantType, Form()],
    redirect_uri: Annotated[str | None, Form()] = None,
    code: Annotated[str | None, Form()] = None,
    refresh_token: Annotated[str | None, Form()] = None,
    code_verifier: Annotated[str | None, Form()] = None,
    use_case=Provide(OAuthTokenUseCase),
) -> Any:
    if app_auth:
        username = app_auth.username
        password = app_auth.password
    else:
        username = None
        password = None

    res = await use_case.execute(
        OAuthTokenCommand(
            grant_type=grant_type,
            redirect_uri=redirect_uri,
            code=code,
            refresh_token=refresh_token,
            code_verifier=code_verifier,
            username=username,
            password=password,
        )
    )
    return res


@router.get("/scopes")
async def get_scopes(
    use_case=Provide(GetAppScopesUseCase),
) -> list[Scope]:
    return use_case.execute()
