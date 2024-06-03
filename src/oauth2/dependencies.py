from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.apps.dependencies import AppsServiceDep
from src.apps.schemas import AppInMongo

from .apps import AuthoritativeAppsService, apps_service
from .exceptions import InvalidAppCredentials
from .service import OAuth2Service, oauth2_service

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


def get_authoritative_apps_service() -> AuthoritativeAppsService:
    return apps_service


AuthoritativeAppsServiceDep = Annotated[
    AuthoritativeAppsService, Depends(get_authoritative_apps_service)
]


def get_oauth2_service() -> OAuth2Service:
    return oauth2_service


OAuth2ServiceDep = Annotated[OAuth2Service, Depends(get_oauth2_service)]
