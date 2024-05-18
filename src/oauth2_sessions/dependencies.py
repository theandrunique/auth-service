from typing import Annotated

from fastapi import Depends

from src.mongo import db

from .repository import OAuth2SessionsRepository
from .service import OAuth2SessionsService

service = OAuth2SessionsService(
    repository=OAuth2SessionsRepository(
        collection=db["oauth2_sessions"],
    )
)


async def get_oauth2_sessions_service() -> OAuth2SessionsService:
    return service


OAuth2SessionsServiceDep = Annotated[
    OAuth2SessionsService, Depends(get_oauth2_sessions_service)
]
