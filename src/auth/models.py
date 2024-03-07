import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class RefreshTokenInDB(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    jti: Mapped[str]
    created_at: Mapped[datetime.datetime]
    last_accessed: Mapped[datetime.datetime]
    ip_address: Mapped[str | None] = mapped_column(nullable=True)
