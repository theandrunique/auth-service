from dataclasses import dataclass

from src.users.entities import User
from src.users.service import IUsersService


@dataclass
class GetMeCommand:
    user: User


@dataclass
class GetMeUseCase:
    users_service: IUsersService

    async def execute(self, command: GetMeCommand) -> User:
        return command.user
