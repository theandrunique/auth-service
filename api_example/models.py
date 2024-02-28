from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class UserInDB(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[bytes]
    active: Mapped[bool] = mapped_column(server_default="TRUE")
    
    
class RefreshTokenInDB(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token_id: Mapped[str] 
    # hashed_token: Mapped[bytes] = mapped_column(nullable=True)
    # scopes: Mapped[str]
