from src.apps.repository import AppsRepository
from src.dependencies import resolve
from src.oauth2_sessions.repository import OAuth2SessionsRepository
from src.sessions.repository import SessionsRepository
from src.users.repository import UsersRepository


async def init_mongo_repositories() -> None:
    repo = resolve(UsersRepository)
    await repo.init()

    repo = resolve(SessionsRepository)
    await repo.init()

    repo = resolve(OAuth2SessionsRepository)
    await repo.init()

    repo = resolve(AppsRepository)
    await repo.init()
