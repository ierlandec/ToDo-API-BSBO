from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models import Task
from schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)


@router.get("", response_model=List[TaskResponse])
async def get_all_tasks(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task))
    return [task.to_dict() for task in result.scalars().all()]


@router.get("/quadrant/{quadrant}", response_model=List[TaskResponse])
async def get_tasks_by_quadrant(quadrant: str, db: AsyncSession = Depends(get_async_session)):
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(status_code=400, detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4")
    cutoff = Task.today() + timedelta(days=3)
    urgency = (
        Task.deadline_at <= cutoff
        if quadrant in ("Q1", "Q3")
        else or_(Task.deadline_at.is_(None), Task.deadline_at > cutoff)
    )
    result = await db.execute(
        select(Task).where(Task.is_important == (quadrant in ("Q1", "Q2")), urgency)
    )
    return [task.to_dict() for task in result.scalars().all()]


@router.get("/search", response_model=List[TaskResponse])
async def search_tasks(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_async_session)):
    keyword = f"%{q.lower()}%"
    result = await db.execute(
        select(Task).where(Task.title.ilike(keyword) | Task.description.ilike(keyword))
    )
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(status_code=404, detail="По данному запросу ничего не найдено")
    return [task.to_dict() for task in tasks]


@router.get("/status/{status}", response_model=List[TaskResponse])
async def get_tasks_by_status(status: str, db: AsyncSession = Depends(get_async_session)):
    if status not in ["completed", "pending"]:
        raise HTTPException(status_code=404, detail="Недопустимый статус. Используйте: completed или pending")
    result = await db.execute(select(Task).where(Task.completed == (status == "completed")))
    return [task.to_dict() for task in result.scalars().all()]


@router.get("/today", response_model=List[TaskResponse])
async def get_tasks_today(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(Task).where(Task.deadline_at == Task.today()).order_by(Task.id)
    )
    return [task.to_dict() for task in result.scalars().all()]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task.to_dict()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_async_session)):
    new_task = Task(
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        deadline_at=task.deadline_at,
        completed=False,
    )
    new_task.sync_deadline_fields()
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task.to_dict()


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    if "completed" in update_data:
        task.completed_at = datetime.now() if task.completed else None
    task.sync_deadline_fields()
    await db.commit()
    await db.refresh(task)
    return task.to_dict()


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_async_session)) -> dict:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    deleted_task_info = {"id": task.id, "title": task.title}
    await db.delete(task)
    await db.commit()
    return {"message": "Задача успешно удалена", **deleted_task_info}


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task.completed = True
    task.completed_at = datetime.now()
    task.sync_deadline_fields()
    await db.commit()
    await db.refresh(task)
    return task.to_dict()
