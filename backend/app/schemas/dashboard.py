from pydantic import BaseModel

from app.schemas.algorithm import AlgorithmSummaryResponse


class DailyActivity(BaseModel):
    date: str
    count: int


class DifficultyBreakdown(BaseModel):
    easy: int
    medium: int
    hard: int


class DashboardResponse(BaseModel):
    streak_count: int
    total_solved: int
    total_attempted: int
    difficulty_breakdown: DifficultyBreakdown
    weekly_activity: list[DailyActivity]
    recommended_algorithm: AlgorithmSummaryResponse | None
