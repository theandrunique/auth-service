from collections.abc import Generator

import jwcrypto
import jwcrypto.common
import jwcrypto.jwk
import punq
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis import Redis
from redis.asyncio import ConnectionPool as RedisConnectionPool

from src.apps.repository import AppsRepository
from src.apps.service import AppsService
from src.config import settings
from src.oauth2_sessions.repository import OAuth2SessionsRepository
from src.oauth2_sessions.service import OAuth2SessionsService
from src.services.base.hash import Hash
from src.services.base.jwe import JWE
from src.services.base.jwt import JWT
from src.services.hash import ImplHash
from src.services.jwe import ImplJWE
from src.services.jwt import ImplJWT
from src.sessions.repository import SessionsRepository
from src.sessions.service import SessionsService
from src.users.repository import UsersRepository
from src.users.service import UsersService
from src.well_known.service import WellKnownService


def create_jwk_keys(private_key_pem: str) -> tuple[jwcrypto.jwk.JWK, jwcrypto.jwk.JWK]:
    private_key = jwcrypto.jwk.JWK.from_pem(private_key_pem.encode())
    public_key = jwcrypto.jwk.JWK()
    public_key.import_key(**jwcrypto.common.json_decode(private_key.export_public()))
    return private_key, public_key


def create_redis_connection_pool() -> RedisConnectionPool:
    return RedisConnectionPool.from_url(settings.RedisURL.unicode_string())


def init_mongodb() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(
        settings.MONGO_URI.unicode_string(),
        uuidRepresentation="standard",
    )
    return client[settings.MONGO_DATABASE_NAME]


def init_container() -> punq.Container:
    container = punq.Container()

    private_key, public_key = create_jwk_keys(settings.PRIVATE_KEY)

    container.register(Hash, ImplHash, scope=punq.Scope.singleton)
    container.register(
        JWT,
        instance=ImplJWT(
            private_key_pem=settings.PRIVATE_KEY,
            public_key_pem=public_key.export_to_pem(),  # type: ignore
            public_key_id=public_key.key_id,  # type: ignore
            algorithm=settings.ALGORITHM,
            issuer=settings.DOMAIN_URL,
            audience=settings.DOMAIN_URL,
        ),
        scope=punq.Scope.singleton,
    )
    container.register(
        JWE,
        instance=ImplJWE(private_key=private_key, public_key=public_key),
        scope=punq.Scope.singleton,
    )

    redis_connection_pool = create_redis_connection_pool()

    def get_redis_client() -> Generator[Redis, None, None]:
        redis = Redis(connection_pool=redis_connection_pool, decode_responses=True)
        yield redis

    container.register(Redis, factory=get_redis_client)

    mongodb = init_mongodb()

    container.register(
        AppsRepository,
        instance=AppsRepository(collection=mongodb["apps"]),
        scope=punq.Scope.singleton,
    )
    container.register(
        OAuth2SessionsRepository,
        instance=OAuth2SessionsRepository(collection=mongodb["oauth2_sessions"]),
        scope=punq.Scope.singleton,
    )
    container.register(
        SessionsRepository,
        instance=SessionsRepository(collection=mongodb["sessions"]),
        scope=punq.Scope.singleton,
    )
    container.register(
        UsersRepository,
        instance=UsersRepository(collection=mongodb["users"]),
        scope=punq.Scope.singleton,
    )

    container.register(AppsService, scope=punq.Scope.singleton)
    container.register(SessionsService, scope=punq.Scope.singleton)
    container.register(OAuth2SessionsService, scope=punq.Scope.singleton)
    container.register(UsersService, scope=punq.Scope.singleton)
    container.register(
        WellKnownService,
        instance=WellKnownService(private_key=private_key),
        scope=punq.Scope.singleton,
    )

    return container


container = init_container()
