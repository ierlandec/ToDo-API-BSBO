from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from utils import today_moscow, determine_quadrant, calculate_days_until_deadline, calculate_urgency


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,  # Первичный ключ
        index=True,  # Создать индекс для быстрого поиска
        autoincrement=True,  # Автоматическая генерация
    )

    title = Column(
        Text,  # Text = текст неограниченной длины
        nullable=False,  # Не может быть NULL
    )

    description = Column(
        Text,
        nullable=True,  # Может быть NULL
    )

    is_important = Column(
        Boolean,
        nullable=False,
        default=False,  # По умолчанию False
    )

    deadline_at = Column(Date, nullable=True)
    _is_urgent = Column("is_urgent", Boolean, nullable=True, default=False)

    quadrant = Column(
        String(2),  # Максимум 2 символа: "Q1", "Q2", "Q3", "Q4"
        nullable=False,
    )

    completed = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=True),  # С поддержкой часовых поясов
        server_default=func.now(),  # Автоматически текущее время
        nullable=False,
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,  # NULL пока задача не завершена
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner = relationship(
        "User",
        back_populates="tasks",
    )

    @staticmethod
    def today():
        # Сроки считаются по календарным дням московского времени.
        return today_moscow()

    @property
    def days_remaining(self):
        return calculate_days_until_deadline(self.deadline_at, self.today())

    @property
    def is_urgent(self):
        return calculate_urgency(self.deadline_at, self.today())

    @is_urgent.setter
    def is_urgent(self, value):
        self._is_urgent = value

    @property
    def calculated_quadrant(self):
        return determine_quadrant(self.is_important, self.is_urgent)

    def sync_deadline_fields(self):
        # Записываем расчётные значения в столбцы БД.
        self._is_urgent = self.is_urgent
        self.quadrant = self.calculated_quadrant

    @property
    def status_message(self):
        if self.deadline_at is None:
            return "Срок не указан"
        if self.completed:
            if self.completed_at is None:
                return "Задача выполнена"
            if self.completed_at.date() <= self.deadline_at:
                return "Задача выполнена в срок"
            return "Задача выполнена с опозданием"
        days = self.days_remaining
        if days < 0:
            return f"Задача просрочена на {abs(days)} дн."
        if days == 0:
            return "Срок выполнения сегодня"
        return f"До дедлайна осталось дней: {days}"

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', quadrant='{self.calculated_quadrant}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "is_important": self.is_important,
            "is_urgent": self.is_urgent,
            "deadline_at": self.deadline_at,
            "days_remaining": self.days_remaining,
            "days_until_deadline": self.days_remaining,
            "status_message": self.status_message,
            "quadrant": self.calculated_quadrant,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
