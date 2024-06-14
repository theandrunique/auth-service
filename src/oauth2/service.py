from dataclasses import dataclass
from uuid import UUID, uuid4

from src.auth.exceptions import InvalidSession
from src.oauth2.exceptions import InvalidRequest
from src.oauth2_sessions.schemas import OAuth2SessionCreate
from src.oauth2_sessions.service import OAuth2SessionsService
from src.services.base.jwe import JWE
from src.services.base.jwt import JWT
from src.users.schemas import UserSchema

from .authoritative_apps import AuthoritativeAppsService
from .repository import AuthorizationRequestsRepository
from .schemas import (
    AccessTokenPayload,
    AuthorizationRequest,
    CodeChallengeMethod,
    CodeExchangeResponse,
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
    jwt: JWT
    jwe: JWE

    async def create_request(
        self,
        client_id: UUID,
        client_secret: UUID,
        user: UserSchema,
        requested_scopes: list[str],
        redirect_uri: str,
        code_challenge_method: CodeChallengeMethod | None,
        code_challenge: str | None,
    ) -> str:
        code = gen_authorization_code()
        req = AuthorizationRequest(
            client_id=client_id,
            client_secret=client_secret,
            user=user,
            requested_scopes=requested_scopes,
            redirect_uri=redirect_uri,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
        )
        await self.requests_repository.add(key=code, item=req)
        return code

    async def validate_code_exchange_request(
        self, key: str
    ) -> AuthorizationRequest | None:
        return await self.requests_repository.get(key)

    async def handle_authorization_code_with_pkce(
        self,
        code_verifier: str,
        req: AuthorizationRequest,
    ) -> CodeExchangeResponse:
        if not req.code_challenge or not req.code_challenge_method:
            raise InvalidRequest()

        if not verify_code_verifier(
            challenge=req.code_challenge,
            method=req.code_challenge_method.value,
            verifier=code_verifier,
        ):
            raise InvalidRequest()

        return await self.create_session_and_tokens(req)

    async def handle_authorization_code(
        self, req: AuthorizationRequest
    ) -> CodeExchangeResponse:
        return await self.create_session_and_tokens(req)

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

    async def handle_refresh(self, token: str) -> CodeExchangeResponse:
        try:
            jti_bytes = self.jwe.decode(token)
            if not jti_bytes:
                raise InvalidSession()
            jti = UUID(bytes=jti_bytes)
        except ValueError:
            raise InvalidSession()

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
