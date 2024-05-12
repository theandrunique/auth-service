from typing import Annotated

from fastapi import Depends

from src.mongo import db

from .repository import UsersRepository
from .service import UsersService

service = UsersService(
    repository=UsersRepository(
        collection=db["users"],
    )
)


def get_users_service() -> UsersService:
    return service


UsersServiceDep = Annotated[UsersService, Depends(get_users_service)]
