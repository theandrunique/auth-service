import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class OAuth2SessionsInDB(Base):
    __tablename__ = "oauth2_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    refresh_token_hash: Mapped[bytes] = mapped_column(index=True)
    session_id: Mapped[UUID]
    app_id: Mapped[UUID]
    scope: Mapped[str]
    last_used: Mapped[datetime.datetime]
    created_at: Mapped[datetime.datetime]
