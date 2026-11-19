from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import date, datetime


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название задачи")
    description: Optional[str] = Field(None, max_length=500, description="Описание задачи")
    is_important: bool = Field(..., description="Важность задачи")
    deadline_at: Optional[date] = Field(None, description="Плановая дата выполнения, YYYY-MM-DD")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_important: Optional[bool] = None
    deadline_at: Optional[date] = Field(None, description="Новая дата дедлайна, YYYY-MM-DD")
    completed: Optional[bool] = None

    @field_validator("title", "is_important", "completed")
    @classmethod
    def reject_explicit_null(cls, value):
        # Пропущенные поля остаются без изменений; описание и дедлайн можно очистить.
        if value is None:
            raise ValueError("Поле не может быть null")
        return value


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deadline_at: Optional[date] = None
    is_urgent: bool
    days_remaining: Optional[int] = Field(None, description="Дней до дедлайна; отрицательное число — просрочка")
    days_until_deadline: Optional[int] = None
    status_message: str
    quadrant: str
    completed: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None


class TaskDeadlineResponse(BaseModel):
    title: str
    description: Optional[str] = None
    created_at: datetime
    deadline_at: Optional[date] = None
    days_remaining: Optional[int] = None


class TimingStatsResponse(BaseModel):
    completed_on_time: int = Field(..., description="Завершены в срок")
    completed_late: int = Field(..., description="Завершены с опозданием")
    on_plan_pending: int = Field(..., description="Незавершённые, срок не истёк")
    overtime_pending: int = Field(..., description="Просроченные незавершённые")
