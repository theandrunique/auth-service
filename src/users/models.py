import datetime

from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class UserInDB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[bytes]
    created_at: Mapped[datetime.datetime]
    active: Mapped[bool] = mapped_column(default=True)
