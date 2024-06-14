from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.apps.schemas import AppInMongo
from src.dependencies import Container, Provide

basic_auth = HTTPBasic()


async def get_app_auth(
    apps_service=Provide(Container.AppsService),
    credentials: HTTPBasicCredentials = Security(basic_auth),
) -> AppInMongo | None:
    try:
        client_id = UUID(credentials.username)
        client_secret = UUID(credentials.password)
    except ValueError:
        return None

    found = await apps_service.get_by_client_id(client_id)
    if not found:
        return None

    if client_secret != found.client_secret:
        return None

    return found


AppAuth = Annotated[AppInMongo, Depends(get_app_auth)]
