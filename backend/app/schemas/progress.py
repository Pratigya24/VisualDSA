from datetime import datetime

from pydantic import BaseModel, Field

from app.models.progress import ProgressStatus


class ProgressUpsertRequest(BaseModel):
    algorithm_id: str
    status: ProgressStatus
    time_spent_ms: int | None = Field(default=None, ge=0)
    hint_used: bool = False


class ProgressResponse(BaseModel):
    algorithm_id: str
    status: ProgressStatus
    attempts: int
    best_time_ms: int | None
    hints_used: int
    last_attempt_at: datetime | None
    solved_at: datetime | None
