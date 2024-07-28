from dataclasses import dataclass
from uuid import UUID

from src.apps.service import IAppsService
from src.auth.exceptions import InvalidSession
from src.auth.service import IAuthService
from src.config import settings
from src.oauth2.exceptions import (
    InvalidAuthorizationCode,
    InvalidClientId,
    InvalidCodeVerifier,
    InvalidRedirectUri,
    NotMatchingConfiguration,
)
from src.oauth2.utils import verify_code_verifier
from src.oauth2_sessions.dto import CreateOAuth2SessionDTO
from src.oauth2_sessions.service import IOAuthSessionsService
from src.schemas import Scope
from src.services.oauth_auth_requests import IAuthReqService

from .dto import RequestValidateResponseDTO, TokenResponseDTO
from .entities import AuthorizationRequest, CodeChallengeMethod, GrantType, ResponseMode, ResponseType
from .responses import RedirectUri, WebMessage
from .service import OAuthService


@dataclass
class OAuthRequestCommand:
    session_token: str

    response_type: ResponseType
    client_id: UUID
    redirect_uri: str
    response_mode: ResponseMode
    scope: list[str]
    state: str | None
    code_challenge: str | None
    code_challenge_method: CodeChallengeMethod | None


@dataclass
class OAuthRequestUseCase:
    oauth_service: OAuthService
    auth_service: IAuthService
    apps_service: IAppsService
    requests_service: IAuthReqService

    async def execute(self, command: OAuthRequestCommand) -> RequestValidateResponseDTO:
        self.command = command
        application = await self.apps_service.get_by_client_id(command.client_id)
        if not application:
            raise InvalidClientId

        if command.redirect_uri not in application.redirect_uris:
            raise NotMatchingConfiguration
        if command.response_mode == ResponseMode.web_message and not application.is_web_message_allowed:
            raise NotMatchingConfiguration

        return RequestValidateResponseDTO(
            app_name=application.name,
            app_description=application.description,
            requested_scopes=self.get_requested_scopes(command.scope),
        )

    def get_requested_scopes(self, scopes: list[str]) -> list[Scope]:
        app_scopes = self.oauth_service.get_app_scopes()
        return [scope for scope in app_scopes if scope.name in scopes]


@dataclass
class OAuthAuthorizeCommand:
    session_token: str

    response_type: ResponseType
    client_id: UUID
    redirect_uri: str
    scope: list[str]
    state: str | None
    response_mode: ResponseMode
    code_challenge: str | None
    code_challenge_method: CodeChallengeMethod | None


@dataclass
class OAuthAuthorizeUseCase:
    oauth_service: OAuthService
    auth_service: IAuthService
    apps_service: IAppsService
    requests_service: IAuthReqService

    async def execute(self, command: OAuthAuthorizeCommand) -> RedirectUri | WebMessage:
        application = await self.apps_service.get_by_client_id(command.client_id)
        if not application:
            raise InvalidClientId

        if command.redirect_uri not in application.redirect_uris:
            raise NotMatchingConfiguration
        if command.response_mode == ResponseMode.web_message and not application.is_web_message_allowed:
            raise NotMatchingConfiguration

        try:
            user, _ = await self.auth_service.validate_session(command.session_token)
        except InvalidSession:
            return await self._handle_error(
                command.response_mode, command.redirect_uri, "login_required", command.state
            )

        if not self.oauth_service.validate_scopes(application.scopes, command.scope):
            return await self._handle_error(command.response_mode, command.redirect_uri, "invalid_scope", command.state)

        if command.response_type == ResponseType.token:
            access_token = self.oauth_service.create_access_token(
                user_id=user.id,
                scopes=command.scope,
                client_id=str(command.client_id),
            )
            return (
                RedirectUri(command.redirect_uri)
                .add_fragment("access_token", access_token)
                .add_fragment("token_type", "Bearer")
                .add_fragment("expires_in", str(settings.ACCESS_TOKEN_EXPIRE_SECONDS))
                .add_fragment("state", command.state)
            )

        new_request = AuthorizationRequest(
            application=application,
            requested_scopes=command.scope,
            redirect_uri=command.redirect_uri,
            user=user,
            state=command.state,
            nonce=None,
            code_challenge=command.code_challenge,
            code_challenge_method=command.code_challenge_method,
            prompt=None,
        )
        code = await self.requests_service.create_new_request(new_request)

        if command.response_type == ResponseType.code:
            return RedirectUri(command.redirect_uri).add_param("code", code).add_param("state", command.state)

        raise NotImplementedError

    async def _handle_error(
        self, response_mode: ResponseMode, target_origin: str, error: str, state: str | None = None
    ) -> WebMessage | RedirectUri:
        if response_mode == ResponseMode.web_message:
            return WebMessage(target_origin, state).add_error(error)
        else:
            return RedirectUri(target_origin).add_param("state", state).add_param("error", error)


@dataclass
class OAuthTokenCommand:
    grant_type: GrantType
    redirect_uri: str | None = None
    code: str | None = None
    refresh_token: str | None = None
    code_verifier: str | None = None
    username: str | None = None
    password: str | None = None


@dataclass
class OAuthTokenUseCase:
    oauth_service: OAuthService
    sessions_service: IOAuthSessionsService
    requests_service: IAuthReqService

    async def execute(self, command: OAuthTokenCommand) -> TokenResponseDTO:
        if command.grant_type == GrantType.refresh_token:
            return await self._execute_refresh_token(command)
        elif command.grant_type == GrantType.authorization_code:
            return await self._execute_token_exchange(command)

        raise NotImplementedError

    async def _execute_refresh_token(self, command: OAuthTokenCommand) -> TokenResponseDTO:
        session = await self.oauth_service.validate_refresh_token(command.refresh_token)
        token_id = await self.sessions_service.update_token_id(session_id=session.id)
        return self.create_tokens(
            user_id=session.user_id,
            scopes=session.scopes,
            client_id=session.client_id,
            token_id=token_id,
        )

    async def _execute_token_exchange(self, command: OAuthTokenCommand) -> TokenResponseDTO:
        if not command.code:
            raise InvalidAuthorizationCode

        req = await self.requests_service.get(code=command.code)

        if req.redirect_uri != command.redirect_uri:
            raise InvalidRedirectUri

        if req.code_challenge and req.code_challenge_method:
            if not command.code_verifier:
                raise InvalidCodeVerifier

            if not verify_code_verifier(
                challenge=req.code_challenge,
                method=req.code_challenge_method,
                verifier=command.code_verifier,
            ):
                raise InvalidCodeVerifier
        else:
            self.oauth_service.validate_client_credentials(req.application, command.username, command.password)

        session = await self.sessions_service.create_new_session(
            CreateOAuth2SessionDTO(
                user_id=req.user.id,
                client_id=req.application.client_id,
                scopes=req.requested_scopes,
            )
        )
        return self.create_tokens(
            user_id=req.user.id,
            scopes=req.requested_scopes,
            client_id=req.application.client_id,
            token_id=session.token_id,
        )

    def create_tokens(self, user_id: UUID, scopes: list[str], client_id: UUID, token_id: UUID) -> TokenResponseDTO:
        access_token = self.oauth_service.create_access_token(
            user_id=user_id,
            scopes=scopes,
            client_id=str(client_id),
        )
        refresh_token = self.oauth_service.create_refresh_token(token_id)

        return TokenResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            scopes=scopes,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        )


@dataclass
class GetAppScopesUseCase:
    oauth_service: OAuthService

    def execute(self) -> list[Scope]:
        return self.oauth_service.get_app_scopes()
