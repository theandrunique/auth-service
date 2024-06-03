from dataclasses import dataclass
from uuid import UUID

from src.auth.exceptions import InvalidSession
from src.oauth2_sessions.dependencies import service as oauth2_sessions
from src.oauth2_sessions.schemas import OAuth2SessionCreate
from src.oauth2_sessions.service import OAuth2SessionsService
from src.users.schemas import UserSchema

from .repository import AuthorizationRequestsRepository
from .schemas import AuthorizationRequest, CodeExchangeResponse, RefreshTokenPayload
from .utils import create_token_pair, gen_authorization_code


@dataclass(kw_only=True)
class OAuth2Service:
    repository: AuthorizationRequestsRepository
    oauth2_sessions: OAuth2SessionsService

    async def create_request(
        self,
        client_id: UUID,
        client_secret: UUID,
        user: UserSchema,
        requested_scopes: list[str],
        redirect_uri: str,
    ) -> str:
        code = gen_authorization_code()
        req = AuthorizationRequest(
            client_id=client_id,
            client_secret=client_secret,
            user=user,
            requested_scopes=requested_scopes,
            redirect_uri=redirect_uri,
        )
        await self.repository.add(key=code, item=req)
        return code

    async def validate_request(self, key: str) -> AuthorizationRequest | None:
        return await self.repository.get(key)

    async def handle_request(self, req: AuthorizationRequest) -> CodeExchangeResponse:
        access_token, refresh_token, jti = create_token_pair(
            sub=req.user.id,
            scopes=req.requested_scopes,
            aud=str(req.client_id),
        )
        await oauth2_sessions.add(
            OAuth2SessionCreate(
                app_id=req.client_id,
                refresh_token_id=jti,
                scopes=req.requested_scopes,
                user_id=req.user.id,
            )
        )
        return CodeExchangeResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            scopes=req.requested_scopes,
        )

    async def handle_refresh(
        self, refresh_token_payload: RefreshTokenPayload
    ) -> CodeExchangeResponse:
        session = await oauth2_sessions.get_by_jti(refresh_token_payload.jti)
        if not session:
            raise InvalidSession()
        access_token, refresh_token, jti = create_token_pair(
            sub=session.user_id,
            scopes=session.scopes,
            aud=str(session.app_id),
        )
        await oauth2_sessions.update_jti(id=session.id, new_jti=jti)

        return CodeExchangeResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            scopes=session.scopes,
        )


oauth2_service = OAuth2Service(
    repository=AuthorizationRequestsRepository(), oauth2_sessions=oauth2_sessions
)
