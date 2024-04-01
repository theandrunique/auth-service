
from typing import Annotated

from fastapi import Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_user, get_user_optional, get_user_with_session
from src.database import db_helper
from src.sessions.models import UserSessionsInDB
from src.users.models import UserInDB

UserAuthorization = Annotated[UserInDB, Security(get_user)]


UserAuthorizationWithSession = Annotated[
    tuple[UserInDB, UserSessionsInDB], Security(get_user_with_session)
]


UserAuthorizationOptional = Annotated[UserInDB | None, Security(get_user_optional)]


DbSession = Annotated[AsyncSession, Depends(db_helper.session_dependency)]
