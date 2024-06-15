from dataclasses import dataclass
from uuid import UUID, uuid4

from src.apps.schemas import AppInMongo, Scope
from src.apps.service import AppsService
from src.auth.exceptions import InvalidSession
from src.oauth2.exceptions import (
    InvalidAuthorizationCode,
    InvalidClientId,
    InvalidCodeVerifier,
    NotAllowedScope,
    RedirectUriNotAllowed,
)
from src.oauth2_sessions.schemas import OAuth2SessionCreate
from src.oauth2_sessions.service import OAuth2SessionsService
from src.schemas import AuthoritativeApp
from src.services.authoritative_apps import AuthoritativeAppsService
from src.services.base.jwe import JWE
from src.services.base.jwt import JWT
from src.users.schemas import UserSchema

from .repository import AuthorizationRequestsRepository
from .schemas import (
    AccessTokenPayload,
    AuthorizationRequest,
    CodeChallengeMethod,
    CodeExchangeResponse,
    RedirectUriResponse,
    WebMessageResponse,
)
from .utils import (
    gen_authorization_code,
    verify_code_verifier,
)


@dataclass(kw_only=True)
class OAuth2Service:
    requests_repository: AuthorizationRequestsRepository
    oauth2_sessions: OAuth2SessionsService
    authoritative_apps: AuthoritativeAppsService
    apps_service: AppsService
    jwt: JWT
    jwe: JWE

    async def find_app(self, client_id: UUID) -> AppInMongo | AuthoritativeApp | None:
        app = self.authoritative_apps.get_by_client_id(client_id)
        if app:
            return app

        return await self.apps_service.get_by_client_id(client_id)

    def validate_scopes(self, scopes: list[Scope], requested_scopes: list[str]):
        scopes_str = {scope.name for scope in scopes}
        for scope in requested_scopes:
            if scope not in scopes_str:
                return False
        return True

    async def handle_authorize_code(
        self,
        client_id: UUID,
        requested_scopes: list[str],
        redirect_uri: str,
        user: UserSchema,
        state: str | None,
        code_challenge_method: CodeChallengeMethod | None,
        code_challenge: str | None,
    ) -> RedirectUriResponse:
        app = await self.find_app(client_id)
        if not app:
            raise InvalidClientId()

        if redirect_uri not in app.redirect_uris:
            raise RedirectUriNotAllowed()

        if not self.validate_scopes(
            scopes=app.scopes, requested_scopes=requested_scopes
        ):
            raise NotAllowedScope(scopes=requested_scopes)

        code = gen_authorization_code()
        req = AuthorizationRequest(
            client_id=app.client_id,
            client_secret=app.client_secret,
            user=user,
            requested_scopes=requested_scopes,
            redirect_uri=redirect_uri,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
        state = f"&state={state}" if state else ""
        await self.requests_repository.add(key=code, item=req)
        return RedirectUriResponse(
            redirect_uri=f"{redirect_uri}/callback?" f"code={code}" f"{state}"
        )

    async def handle_authorize_token(
        self,
        client_id: UUID,
        redirect_uri: str,
        user: UserSchema,
        requested_scopes: list[str],
        state: str | None,
    ) -> RedirectUriResponse:
        app = await self.find_app(client_id)
        if not app:
            raise InvalidClientId()

        if redirect_uri not in app.redirect_uris:
            raise RedirectUriNotAllowed()

        if not self.validate_scopes(
            scopes=app.scopes, requested_scopes=requested_scopes
        ):
            raise NotAllowedScope(scopes=requested_scopes)

        access_token = self.create_access_token(
            user_id=user.id,
            scopes=requested_scopes,
            client_id=str(app.client_id),
        )

        return RedirectUriResponse(
            redirect_uri=f"{redirect_uri}/callback?"
            + f"access_token={access_token}"
            + f"&state={state}"
            if state
            else ""
        )

    async def handle_authorize_web_message(
        self,
        client_id: UUID,
        redirect_uri: str,
        user: UserSchema,
        requested_scopes: list[str],
        state: str | None,
        code_challenge_method: CodeChallengeMethod | None,
        code_challenge: str | None,
    ) -> WebMessageResponse:
        app = self.authoritative_apps.get_by_client_id(client_id)
        if not app:
            raise InvalidClientId()

        if redirect_uri not in app.redirect_uris:
            raise RedirectUriNotAllowed()

        if not self.validate_scopes(
            scopes=app.scopes, requested_scopes=requested_scopes
        ):
            raise NotAllowedScope(scopes=requested_scopes)

        code = gen_authorization_code()
        req = AuthorizationRequest(
            client_id=app.client_id,
            client_secret=app.client_secret,
            user=user,
            requested_scopes=requested_scopes,
            redirect_uri=redirect_uri,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
        await self.requests_repository.add(key=code, item=req)

        return WebMessageResponse(code=code, state=state)

    async def handle_code_exchange(
        self, code: str, redirect_uri: str
    ) -> CodeExchangeResponse:
        req = await self.requests_repository.get(key=code)
        if not req:
            raise InvalidAuthorizationCode()

        if req.redirect_uri != redirect_uri:
            raise RedirectUriNotAllowed()

        return await self.create_session_and_tokens(req)

    async def handle_code_exchange_pkce(
        self, code: str, redirect_uri: str, code_verifier: str
    ) -> CodeExchangeResponse:
        req = await self.requests_repository.get(key=code)
        if not req:
            raise InvalidAuthorizationCode()

        if req.redirect_uri != redirect_uri:
            raise RedirectUriNotAllowed()

        if not req.code_challenge or not req.code_challenge_method:
            raise InvalidCodeVerifier()

        if not verify_code_verifier(
            challenge=req.code_challenge,
            method=req.code_challenge_method.value,
            verifier=code_verifier,
        ):
            raise InvalidCodeVerifier()

        return await self.create_session_and_tokens(req)

    async def handle_refresh_token(self, refresh_token: str) -> CodeExchangeResponse:
        jwe = self.jwe.decode(refresh_token)
        if not jwe:
            raise InvalidSession()
        jti = UUID(bytes=jwe)

        session = await self.oauth2_sessions.get_by_jti(jti)
        if not session:
            raise InvalidSession()

        new_jti = uuid4()
        access_token = self.create_access_token(
            user_id=session.user_id,
            scopes=session.scopes,
            client_id=str(session.client_id),
        )
        refresh_token = self.jwe.encode(new_jti.bytes)

        await self.oauth2_sessions.update_jti(id=session.id, new_jti=new_jti)
        return CodeExchangeResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            scopes=session.scopes,
        )

    def create_access_token(
        self, user_id: UUID, scopes: list[str], client_id: str
    ) -> str:
        return self.jwt.encode(
            payload=AccessTokenPayload(
                sub=user_id,
                scopes=scopes,
                aud=client_id,
            ).model_dump()
        )

    async def create_session_and_tokens(
        self, req: AuthorizationRequest
    ) -> CodeExchangeResponse:
        jti = uuid4()
        await self.oauth2_sessions.add(
            OAuth2SessionCreate(
                user_id=req.user.id,
                refresh_token_id=jti,
                client_id=req.client_id,
                scopes=req.requested_scopes,
            )
        )
        access_token = self.create_access_token(
            user_id=req.user.id,
            scopes=req.requested_scopes,
            client_id=str(req.client_id),
        )
        refresh_token = self.jwe.encode(jti.bytes)
        return CodeExchangeResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            scopes=req.requested_scopes,
        )
