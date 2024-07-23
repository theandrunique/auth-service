from uuid import UUID, uuid4

from src.users.entities import User
from src.users.repository import IUsersRepository


class InMemoryUsersRepository(IUsersRepository):
    def __init__(self):
        self.users: dict[UUID, User] = {}

    async def add(self, user: User) -> User:
        if user.id is None:
            user.id = uuid4()
        self.users[user.id] = user
        return user

    async def get_all(self, count: int, offset: int) -> list[User]:
        return list(self.users.values())[offset : offset + count]

    async def get_by_id(self, id: UUID) -> User | None:
        return self.users.get(id)

    async def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    async def get_by_username(self, username: str) -> User | None:
        return next((user for user in self.users.values() if user.username == username), None)

    async def update_username(self, id: UUID, new_username: str) -> User:
        user = self.users[id]
        user.username = new_username
        return user

    async def update_password(self, id: UUID, new_password_hash: bytes) -> User:
        user = self.users[id]
        user.hashed_password = new_password_hash
        return user

    async def change_active_status(self, id: UUID, new_status: bool) -> User:
        user = self.users[id]
        user.active = new_status
        return user
