from typing import List
from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import Date, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models import Task
from schemas import TaskDeadlineResponse, TimingStatsResponse

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/", response_model=dict)
async def get_tasks_stats(db: AsyncSession = Depends(get_async_session)) -> dict:
    urgent = Task.deadline_at <= Task.today() + timedelta(days=3)
    quadrant = case(
        (Task.is_important.is_(True), case((urgent, "Q1"), else_="Q2")),
        else_=case((urgent, "Q3"), else_="Q4"),
    )
    # Счётчики вычисляются в PostgreSQL без загрузки всех задач в Python.
    statement = select(
        func.count(Task.id).label("total"),
        *(func.count(case((quadrant == q, 1))).label(q) for q in ("Q1", "Q2", "Q3", "Q4")),
        func.count(case((Task.completed.is_(True), 1))).label("completed"),
        func.count(case((Task.completed.is_(False), 1))).label("pending"),
    )
    row = (await db.execute(statement)).one()._mapping
    return {
        "total_tasks": row["total"],
        "by_quadrant": {q: row[q] for q in ("Q1", "Q2", "Q3", "Q4")},
        "by_status": {"completed": row["completed"], "pending": row["pending"]},
    }


@router.get("/timing", response_model=TimingStatsResponse)
async def get_deadline_stats(db: AsyncSession = Depends(get_async_session)):
    today = Task.today()
    # DATE означает весь день: задача с сегодняшним дедлайном ещё не просрочена.
    completion_date = cast(Task.completed_at, Date)
    statement = select(
        func.count(case(((Task.completed.is_(True)) & (completion_date <= Task.deadline_at), 1))).label("completed_on_time"),
        func.count(case(((Task.completed.is_(True)) & (completion_date > Task.deadline_at), 1))).label("completed_late"),
        func.count(case(((Task.completed.is_(False)) & (Task.deadline_at >= today), 1))).label("on_plan_pending"),
        func.count(case(((Task.completed.is_(False)) & (Task.deadline_at < today), 1))).label("overtime_pending"),
    )
    row = (await db.execute(statement)).one()._mapping
    return TimingStatsResponse(**dict(row))


@router.get("/deadlines", response_model=List[TaskDeadlineResponse])
async def get_pending_deadlines(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(Task)
        .where(Task.completed.is_(False))
        .order_by(Task.deadline_at.asc().nulls_last(), Task.id)
    )
    return [
        {
            "title": task.title,
            "description": task.description,
            "created_at": task.created_at,
            "deadline_at": task.deadline_at,
            "days_remaining": task.days_remaining,
        }
        for task in result.scalars().all()
    ]
