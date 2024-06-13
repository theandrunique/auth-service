from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.apps.schemas import AppInMongo
from src.dependencies import Container, Provide

from .apps import AuthoritativeAppsService, apps_service
from .exceptions import InvalidAppCredentials

basic_auth = HTTPBasic()


async def get_app_auth(
    apps_service=Provide(Container.AppsService),
    credentials: HTTPBasicCredentials = Security(basic_auth),
) -> AppInMongo:
    client_id = credentials.username
    client_secret = credentials.password
    found = await apps_service.get_by_client_id(UUID(client_id))
    if not found:
        raise InvalidAppCredentials()

    if UUID(hex=client_secret) != found.client_secret:
        raise InvalidAppCredentials()

    return found


AppAuth = Annotated[AppInMongo, Depends(get_app_auth)]


def get_authoritative_apps_service() -> AuthoritativeAppsService:
    return apps_service


AuthoritativeAppsServiceDep = Annotated[
    AuthoritativeAppsService, Depends(get_authoritative_apps_service)
]
