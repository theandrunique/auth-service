import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class ApplicationInDB(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    client_id: Mapped[str]
    client_secret: Mapped[str]
    name: Mapped[str]
    description: Mapped[str]
    website: Mapped[str]
    redirect_uris: Mapped[str]
    created_at: Mapped[datetime.datetime]
    scopes: Mapped[str]
