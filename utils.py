from datetime import date, datetime, timedelta, timezone
from typing import Optional


def today_moscow() -> date:
    return datetime.now(timezone(timedelta(hours=3))).date()


def calculate_days_until_deadline(deadline_at: Optional[date], today: Optional[date] = None) -> Optional[int]:
    if deadline_at is None:
        return None
    return (deadline_at - (today if today is not None else today_moscow())).days


def calculate_urgency(deadline_at: Optional[date], today: Optional[date] = None) -> bool:
    days = calculate_days_until_deadline(deadline_at, today)
    return days is not None and days <= 3


def determine_quadrant(is_important: bool, is_urgent: bool) -> str:
    if is_important:
        return "Q1" if is_urgent else "Q2"
    return "Q3" if is_urgent else "Q4"
