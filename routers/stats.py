from fastapi import APIRouter
from database import tasks_db


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
async def get_tasks_stats() -> dict:
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}

    for task in tasks_db:
        by_quadrant[task["quadrant"]] += 1
        status = "completed" if task["completed"] else "pending"
        by_status[status] += 1

    return {
        "total_tasks": len(tasks_db),
        "by_quadrant": by_quadrant,
        "by_status": by_status,
    }
