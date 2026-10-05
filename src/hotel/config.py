import os

def get_allowed_statuses() -> list[str]:
    statuses = os.getenv("ALLOWED_STATUSES", "pending,confirmed,cancelled")
    return [s.strip() for s in statuses.split(",")]