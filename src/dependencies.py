from typing import Annotated

from fastapi import Security

from src.auth.dependencies import get_user, get_user_optional, get_user_with_session
from src.database import DbSession as DbSession  # noqa
from src.sessions.models import UserSessionsInDB
from src.users.models import UserInDB

UserAuthorization = Annotated[UserInDB, Security(get_user)]


UserAuthorizationWithSession = Annotated[
    tuple[UserInDB, UserSessionsInDB], Security(get_user_with_session)
]


UserAuthorizationOptional = Annotated[UserInDB | None, Security(get_user_optional)]
