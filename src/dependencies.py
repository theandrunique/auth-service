from fastapi import params
from redis.asyncio import Redis

from src.container import container
from src.services.base import hash, jwe, jwt


class Container:
    JWT = jwt.JWT
    JWE = jwe.JWE
    Hash = hash.Hash
    Redis = Redis


def Provide[T](
    dependency: type[T],
) -> T:
    def _dependency():
        return container.resolve(dependency)

    return params.Depends(dependency=_dependency, use_cache=True)  # type: ignore


def resolve[T](dependency: type[T]) -> T:
    return container.resolve(dependency)  # type: ignore
