import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from database import AsyncSessionLocal
from models import Task

logger = logging.getLogger(__name__)


async def update_task_urgency():
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Task).where(Task.completed.is_(False)))
            updated_count = 0
            for task in result.scalars().all():
                urgency = task.is_urgent
                quadrant = task.calculated_quadrant
                if task._is_urgent != urgency or task.quadrant != quadrant:
                    task.sync_deadline_fields()
                    updated_count += 1
            if updated_count:
                await db.commit()
            print(f"Обновление срочности: изменено задач — {updated_count}")
            return updated_count
        except Exception:
            await db.rollback()
            logger.exception("Не удалось обновить срочность задач")
            raise


def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        update_task_urgency,
        trigger="cron",
        hour=9,
        minute=0,
        id="update_urgency",
        name="Обновление срочности задач",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.start()
    print("Планировщик запущен: ежедневно в 09:00 по Москве")
    return scheduler
