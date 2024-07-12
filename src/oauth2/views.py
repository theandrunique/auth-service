from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from src.dependencies import Provide
from src.oauth2.entities import CodeChallengeMethod, GrantType, ResponseType
from src.oauth2.responses import RedirectUri, WebMessage
from src.oauth2.use_cases import (
    GetAppScopesUseCase,
    OAuthAuthorizeCommand,
    OAuthAuthorizeUseCase,
    OAuthTokenCommand,
    OAuthTokenUseCase,
)
from src.schemas import Scope
from src.sessions.dependencies import SessionCookie

from .dependencies import AppAuth
from .schemas import CodeExchangeResponseSchema

router = APIRouter(prefix="/oauth", tags=["oauth2"])


@router.get("/authorize", response_model_exclude_none=True)
async def oauth2_authorize(
    session_token: SessionCookie,
    response_type: Annotated[ResponseType, Query()],
    client_id: Annotated[UUID, Query()],
    redirect_uri: Annotated[str, Query()],
    scope: Annotated[list[str], Query(default_factory=list)],
    state: Annotated[str | None, Query()] = None,
    code_challenge_method: Annotated[CodeChallengeMethod | None, Query()] = None,
    code_challenge: Annotated[str | None, Query()] = None,
    use_case=Provide(OAuthAuthorizeUseCase),
) -> Any:
    res = await use_case.execute(
        OAuthAuthorizeCommand(
            session_token=session_token.token if session_token else "",
            response_type=response_type,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
    )
    if isinstance(res, RedirectUri):
        return RedirectResponse(url=res.build())
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
