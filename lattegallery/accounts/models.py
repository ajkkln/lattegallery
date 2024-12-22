import typing
from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lattegallery.core.db import Base

if typing.TYPE_CHECKING:
    from lattegallery.pictures.models import Picture


class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    MAIN_ADMIN = "MAIN_ADMIN"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    name: Mapped[str]
    role: Mapped[Role]

    pictures: Mapped[list["Picture"]] = relationship(back_populates="owner")