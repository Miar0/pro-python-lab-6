import os
import datetime

def get_allowed_statuses() -> list[str]:
    statuses = os.getenv("ALLOWED_STATUSES", "pending,confirmed,cancelled")
    return [s.strip() for s in statuses.split(",")]

def get_current_date() -> str:
    """Для тестування deterministic time."""
    return datetime.date.today().isoformat()