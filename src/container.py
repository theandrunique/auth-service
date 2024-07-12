import glob
import json
import os
from uuid import UUID

import jwcrypto
import jwcrypto.common
import jwcrypto.jwk
import punq
from beanie import init_beanie
from jwcrypto import jwk
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
from src.logger import logger
from src.oauth2.req_service import AuthorizationRequestsRepository, AuthReqService, IAuthReqRepository
from src.oauth2.service import OAuthService
from src.oauth2.use_cases import GetAppScopesUseCase, OAuthAuthorizeUseCase, OAuthTokenUseCase
from src.oauth2_sessions.models import OAuth2SessionODM
from src.oauth2_sessions.repository import IOAuth2SessionsRepository, MongoOAuth2SessionsRepository
from src.oauth2_sessions.service import IOAuthSessionsService, OAuthSessionsService
from src.schemas import AppScopes, AuthoritativeApp, KeyPair
from src.services.authoritative_apps import AuthoritativeAppsService
from src.services.base.hash import Hash
from src.services.base.jwe import JWE
from src.services.base.jwt import JWT
from src.services.hash import ImplHash
from src.services.jwe import ImplJWE
from src.services.jwt import ImplJWT
from src.services.key_manager import KeyManager
from src.sessions.models import SessionODM
from src.sessions.repository import ISessionsRepository, MongoSessionsRepository
from src.sessions.service import ISessionsService, SessionsService
from src.users.models import UserODM
from src.users.repository import IUsersRepository, MongoUsersRepository
from src.users.service import IUsersService, UsersService
from src.users.use_cases import GetMeUseCase
from src.well_known.service import WellKnownService


def load_certs() -> list[str]:
    certs = []
    try:
        for cert_path in glob.glob(os.path.join(settings.CERT_DIR, "*.pem")):
            with open(cert_path) as f:
                certs.append(f.read())

        if len(certs) == 0:
            raise Exception("No certs were found")
        return certs
    except Exception:
        logger.critical("Failed to load certs: ", exc_info=True)
        raise


def create_jwk_keys_from_certs(certs: list[str]) -> list[tuple[jwk.JWK, jwk.JWK]]:
    jwk_keys = []
    for cert in certs:
        private_key = jwk.JWK.from_pem(cert.encode())
        public_key = jwk.JWK()
        public_key.import_key(**jwcrypto.common.json_decode(private_key.export_public()))
        jwk_keys.append((private_key, public_key))
    return jwk_keys


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


def load_authoritative_apps() -> tuple[dict[UUID, AuthoritativeApp], AppScopes]:
    try:
        with open(settings.AUTHORITATIVE_APPS_PATH) as f:
            apps_dict = json.loads(f.read())
            apps_list = apps_dict["apps"]
            loaded_scopes = apps_dict["scopes"]
            apps_dict = {}
            for app in apps_list:
                loaded_app = AuthoritativeApp(**app)
                apps_dict[loaded_app.client_id] = loaded_app

            app_scopes = AppScopes.model_validate(loaded_scopes)
            return apps_dict, app_scopes
    except Exception as e:
        logger.error("Failed to load authoritative apps: ", exc_info=False)
        raise e


async def init_container() -> punq.Container:
    container = punq.Container()

    certs = load_certs()
    jwk_keys = create_jwk_keys_from_certs(certs)

    key_pairs = [KeyPair(private_key=priv, public_key=pub) for priv, pub in jwk_keys]
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
    container.register(AuthReqService, scope=punq.Scope.singleton)
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

    return container
