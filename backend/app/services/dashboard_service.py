from datetime import datetime, timedelta, timezone

from beanie import PydanticObjectId

from app.models.algorithm import Difficulty
from app.models.progress import ProgressStatus
from app.repositories.algorithm_repository import AlgorithmRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.algorithm import AlgorithmSummaryResponse
from app.schemas.dashboard import DailyActivity, DashboardResponse, DifficultyBreakdown

WEEKLY_ACTIVITY_DAYS = 7


class DashboardService:
    def __init__(
        self,
        progress_repository: ProgressRepository,
        algorithm_repository: AlgorithmRepository,
        analytics_repository: AnalyticsRepository,
        bookmark_repository: BookmarkRepository,
    ) -> None:
        self._progress = progress_repository
        self._algorithms = algorithm_repository
        self._analytics = analytics_repository
        self._bookmarks = bookmark_repository

    async def get_dashboard(self, user_id: PydanticObjectId, streak_count: int) -> DashboardResponse:
        all_progress = await self._progress.list_for_user(user_id)
        solved_records = [p for p in all_progress if p.status == ProgressStatus.SOLVED]
        solved_algorithm_ids = [p.algorithm_id for p in solved_records]
        solved_algorithms = await self._algorithms.get_many_by_ids(solved_algorithm_ids)

        breakdown = DifficultyBreakdown(easy=0, medium=0, hard=0)
        for algorithm in solved_algorithms:
            if algorithm.difficulty == Difficulty.EASY:
                breakdown.easy += 1
            elif algorithm.difficulty == Difficulty.MEDIUM:
                breakdown.medium += 1
            else:
                breakdown.hard += 1

        since = datetime.now(timezone.utc) - timedelta(days=WEEKLY_ACTIVITY_DAYS - 1)
        activity_by_day = await self._analytics.daily_activity_counts(user_id, since)
        weekly_activity = [
            DailyActivity(date=day, count=activity_by_day.get(day, 0))
            for day in self._last_n_dates(WEEKLY_ACTIVITY_DAYS)
        ]

        recommended = await self._recommend_next(user_id, {p.algorithm_id for p in all_progress})

        return DashboardResponse(
            streak_count=streak_count,
            total_solved=len(solved_records),
            total_attempted=len(all_progress),
            difficulty_breakdown=breakdown,
            weekly_activity=weekly_activity,
            recommended_algorithm=recommended,
        )

    @staticmethod
    def _last_n_dates(n: int) -> list[str]:
        today = datetime.now(timezone.utc).date()
        return [(today - timedelta(days=offset)).isoformat() for offset in range(n - 1, -1, -1)]

    async def _recommend_next(
        self, user_id: PydanticObjectId, attempted_ids: set[PydanticObjectId]
    ) -> AlgorithmSummaryResponse | None:
        # Simple, transparent recommendation heuristic for the Foundation
        # scope: the easiest not-yet-attempted problem, ordered by catalog
        # order. A learned/personalized recommender is out of scope until
        # the AI Engine (Module 6) can reason over pattern mastery.
        for difficulty in (Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD):
            items, _ = await self._algorithms.list_paginated(skip=0, limit=50, difficulty=difficulty)
            for algorithm in items:
                if algorithm.id not in attempted_ids:
                    is_bookmarked = await self._bookmarks.exists(user_id, algorithm.id)
                    return AlgorithmSummaryResponse(
                        id=str(algorithm.id),
                        slug=algorithm.slug,
                        title=algorithm.title,
                        difficulty=algorithm.difficulty,
                        topic_id=str(algorithm.topic_id),
                        pattern_tags=algorithm.pattern_tags,
                        companies=algorithm.companies,
                        estimated_minutes=algorithm.estimated_minutes,
                        status=ProgressStatus.NOT_STARTED,
                        is_bookmarked=is_bookmarked,
                    )
        return None
