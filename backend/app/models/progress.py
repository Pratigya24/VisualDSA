from datetime import datetime
from enum import StrEnum

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class ProgressStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
    NEEDS_REVIEW = "needs_review"


class Progress(Document):
    user_id: PydanticObjectId
    algorithm_id: PydanticObjectId
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    attempts: int = 0
    best_time_ms: int | None = None
    hints_used: int = 0
    last_attempt_at: datetime | None = None
    solved_at: datetime | None = None

    class Settings:
        name = "progress"
        indexes = [
            IndexModel([("user_id", 1), ("algorithm_id", 1)], unique=True),
            IndexModel([("user_id", 1), ("status", 1)]),
        ]
