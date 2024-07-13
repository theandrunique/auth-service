import punq
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import ConnectionPool as RedisConnectionPool
from redis.asyncio import Redis

from src.apps.models import AppODM
from src.apps.repository import IAppsRepository, MongoAppsRepository
from src.apps.service import AppsService, IAppsService
from src.apps.use_cases import (
    CreateAppUseCase,
    GetUserAppsUseCase,
    RegenerateClientSecretUseCase,
    UpdateAppInfoUseCase,
)
from src.auth.service import AuthService, IAuthService
from src.auth.use_cases import LoginUseCase, LogoutUseCase, SignUpUseCase
from src.config import settings
from src.oauth2.service import OAuthService
from src.oauth2.use_cases import GetAppScopesUseCase, OAuthAuthorizeUseCase, OAuthTokenUseCase
from src.oauth2_sessions.models import OAuth2SessionODM
from src.oauth2_sessions.repository import IOAuth2SessionsRepository, MongoOAuth2SessionsRepository
from src.oauth2_sessions.service import IOAuthSessionsService, OAuthSessionsService
from src.schemas import AppScopes
from src.services.authoritative_apps import AuthoritativeAppsService
from src.services.emails import EmailService, IEmailService
from src.services.hash import Hash, ImplHash
from src.services.jwe import JWE, ImplJWE
from src.services.jwt import JWT, ImplJWT
from src.services.key_manager import KeyManager
from src.services.oauth_auth_requests import (
    AuthorizationRequestsRepository,
    AuthReqService,
    IAuthReqRepository,
    IAuthReqService,
)
from src.sessions.models import SessionODM
from src.sessions.repository import ISessionsRepository, MongoSessionsRepository
from src.sessions.service import ISessionsService, SessionsService
from src.users.models import UserODM
from src.users.repository import IUsersRepository, MongoUsersRepository
from src.users.service import IUsersService, UsersService
from src.users.use_cases import GetMeUseCase
from src.utils import load_authoritative_apps, load_certs_and_create_key_pairs
from src.well_known.service import WellKnownService
from src.well_known.use_cases import GetJWKsUseCase, GetOpenIdConfigurationUseCase


def create_redis_connection_pool() -> RedisConnectionPool:
    return RedisConnectionPool.from_url(settings.REDIS_URL.unicode_string())


async def init_mongodb() -> None:
    client = AsyncIOMotorClient(
        settings.MONGO_URI.unicode_string(),
    )
    await init_beanie(
        database=client[settings.MONGO_DATABASE_NAME],
        document_models=[
            UserODM,
            SessionODM,
            OAuth2SessionODM,
            AppODM,
        ],
    )


async def init_container() -> punq.Container:
    container = punq.Container()

    key_pairs = load_certs_and_create_key_pairs()
    key_manager = KeyManager(key_pairs=key_pairs)
    container.register(KeyManager, instance=key_manager, scope=punq.Scope.singleton)

    apps, scopes = load_authoritative_apps()

    container.register(Hash, ImplHash, scope=punq.Scope.singleton)
    container.register(
        JWT,
        instance=ImplJWT(
            key_manager=key_manager,
            algorithm=settings.ALGORITHM,
            issuer=settings.DOMAIN_URL,
            audience=settings.DOMAIN_URL,
        ),
        scope=punq.Scope.singleton,
    )
    container.register(
        JWE,
        instance=ImplJWE(key_manager=key_manager),
        scope=punq.Scope.singleton,
    )
    container.register(AppScopes, instance=scopes, scope=punq.Scope.singleton)

    redis_connection_pool = create_redis_connection_pool()

    def get_redis_client() -> Redis:
        return Redis(connection_pool=redis_connection_pool, decode_responses=True)

    container.register(Redis, factory=get_redis_client)

    await init_mongodb()

    container.register(IAppsRepository, MongoAppsRepository, scope=punq.Scope.singleton)
    container.register(IOAuth2SessionsRepository, MongoOAuth2SessionsRepository, scope=punq.Scope.singleton)
    container.register(ISessionsRepository, MongoSessionsRepository, scope=punq.Scope.singleton)
    container.register(IUsersRepository, MongoUsersRepository, scope=punq.Scope.singleton)
    container.register(IAuthReqRepository, AuthorizationRequestsRepository, scope=punq.Scope.singleton)

    container.register(IAppsService, AppsService, scope=punq.Scope.singleton)
    container.register(IAuthService, AuthService, scope=punq.Scope.singleton)
    container.register(OAuthService, scope=punq.Scope.singleton)
    container.register(IEmailService, EmailService, scope=punq.Scope.singleton)
    container.register(IAuthReqService, AuthReqService, scope=punq.Scope.singleton)
    container.register(IOAuthSessionsService, OAuthSessionsService, scope=punq.Scope.singleton)
    container.register(ISessionsService, SessionsService, scope=punq.Scope.singleton)
    container.register(IUsersService, UsersService, scope=punq.Scope.singleton)
    container.register(WellKnownService, scope=punq.Scope.singleton)
    container.register(
        AuthoritativeAppsService,
        instance=AuthoritativeAppsService(apps=apps),
        scope=punq.Scope.singleton,
    )

    container.register(CreateAppUseCase, scope=punq.Scope.transient)
    container.register(GetUserAppsUseCase, scope=punq.Scope.transient)
    container.register(RegenerateClientSecretUseCase, scope=punq.Scope.transient)
    container.register(UpdateAppInfoUseCase, scope=punq.Scope.transient)

    container.register(SignUpUseCase, scope=punq.Scope.transient)
    container.register(LoginUseCase, scope=punq.Scope.transient)
    container.register(LogoutUseCase, scope=punq.Scope.transient)

    container.register(OAuthAuthorizeUseCase, scope=punq.Scope.transient)
    container.register(OAuthTokenUseCase, scope=punq.Scope.transient)
    container.register(GetAppScopesUseCase, scope=punq.Scope.transient)

    container.register(GetMeUseCase, scope=punq.Scope.transient)

    container.register(GetOpenIdConfigurationUseCase, scope=punq.Scope.transient)
    container.register(GetJWKsUseCase, scope=punq.Scope.transient)

    return container
