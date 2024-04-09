from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hash_password: Mapped[str]
    created_at: Mapped[datetime]
    refresh_token: Mapped[str | None] = mapped_column(nullable=True)
