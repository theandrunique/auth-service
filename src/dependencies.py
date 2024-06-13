from fastapi import params
from redis.asyncio import Redis

from src.apps.service import AppsService
from src.container import container
from src.oauth2_sessions.service import OAuth2SessionsService
from src.services.base import hash, jwe, jwt
from src.sessions.service import SessionsService
from src.users.service import UsersService
from src.well_known.service import WellKnownService


class Container:
    JWT = jwt.JWT
    JWE = jwe.JWE
    Hash = hash.Hash
    Redis = Redis

    SessionsService = SessionsService
    AppsService = AppsService
    OAuth2SessionsService = OAuth2SessionsService
    UsersService = UsersService
    WellKnownService = WellKnownService


def Provide[T](
    dependency: type[T],
) -> T:
    def _dependency():
        return container.resolve(dependency)

    return params.Depends(dependency=_dependency, use_cache=True)  # type: ignore


def resolve[T](dependency: type[T]) -> T:
    return container.resolve(dependency)  # type: ignore
