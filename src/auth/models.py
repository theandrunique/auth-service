import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class UserSessionsInDB(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[UUID]
    last_used: Mapped[datetime.datetime]
    ip_address: Mapped[str | None] = mapped_column(nullable=True)
