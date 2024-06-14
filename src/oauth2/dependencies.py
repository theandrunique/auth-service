from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.apps.schemas import AppInMongo
from src.dependencies import Container, Provide

from .authoritative_apps import AuthoritativeApp
from .exceptions import InvalidAppCredentials

basic_auth = HTTPBasic(
    description="Basic authentication for the app. Use the format `client_id:client_secret`",
    auto_error=False,
)


async def get_app_auth(
    apps_service=Provide(Container.AppsService),
    authoritative_apps_service=Provide(Container.AuthoritativeAppsService),
    credentials: HTTPBasicCredentials = Security(basic_auth),
) -> AuthoritativeApp | AppInMongo | None:
    if not credentials:
        return None

    try:
        client_id = UUID(credentials.username)
        client_secret = UUID(credentials.password)
    except ValueError:
        raise InvalidAppCredentials()

    found = authoritative_apps_service.get_by_client_id(client_id)
    if found and client_secret == found.client_secret:
        return found

    found = await apps_service.get_by_client_id(client_id)
    if not found:
        raise InvalidAppCredentials()
    if client_secret != found.client_secret:
        raise InvalidAppCredentials()

    return found


AppAuth = Annotated[AppInMongo, Depends(get_app_auth)]
