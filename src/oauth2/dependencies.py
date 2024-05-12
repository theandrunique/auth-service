from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.apps.dependencies import AppsServiceDep
from src.apps.schemas import AppInMongo

from .exceptions import InvalidAppCredentials

basic_auth = HTTPBasic()


async def get_app_auth(
    service: AppsServiceDep,
    credentials: HTTPBasicCredentials = Security(basic_auth),
) -> AppInMongo:
    client_id = credentials.username
    client_secret = credentials.password
    found = await service.get_by_client_id(UUID(client_id))
    if not found:
        raise InvalidAppCredentials()

    if UUID(hex=client_secret) != found.client_secret:
        raise InvalidAppCredentials()

    return found


AppAuth = Annotated[AppInMongo, Depends(get_app_auth)]
