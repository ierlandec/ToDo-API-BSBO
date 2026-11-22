from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from dependencies import get_current_admin
from models import Task, User
from schemas_auth import AdminUserResponse

router = APIRouter(prefix="/admin", tags=["administration"])


@router.get("/users", response_model=List[AdminUserResponse])
async def get_users(
    db: AsyncSession = Depends(get_async_session),
    current_admin: User = Depends(get_current_admin),
) -> List[AdminUserResponse]:
    task_counts = (
        select(Task.user_id, func.count(Task.id).label("tasks_count"))
        .group_by(Task.user_id)
        .subquery()
    )
    result = await db.execute(
        select(User, func.coalesce(task_counts.c.tasks_count, 0))
        .outerjoin(task_counts, User.id == task_counts.c.user_id)
        .order_by(User.id)
    )
    return [
        AdminUserResponse(
            id=user.id,
            nickname=user.nickname,
            email=user.email,
            role=user.role.value,
            tasks_count=count,
        )
        for user, count in result.all()
    ]
