import enum

from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship

from database import Base


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    nickname = Column(
        String(50),
        unique=True,  # Никнейм должен быть уникальным
        nullable=False,
        index=True,
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password = Column(
        String(255),  # Храним хеш пароля
        nullable=False,
    )

    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.USER,
    )

    # Один пользователь может иметь много задач.
    tasks = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",  # При удалении пользователя удаляются его задачи
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, nickname='{self.nickname}', role='{self.role.value}')>"
