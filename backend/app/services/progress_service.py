from beanie import PydanticObjectId

from app.core.exceptions import NotFoundError
from app.models.analytics_event import AnalyticsEventType
from app.models.progress import ProgressStatus
from app.repositories.algorithm_repository import AlgorithmRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.progress import ProgressResponse, ProgressUpsertRequest


class ProgressService:
    def __init__(
        self,
        progress_repository: ProgressRepository,
        algorithm_repository: AlgorithmRepository,
        analytics_repository: AnalyticsRepository,
    ) -> None:
        self._progress = progress_repository
        self._algorithms = algorithm_repository
        self._analytics = analytics_repository

    async def upsert(
        self, user_id: PydanticObjectId, payload: ProgressUpsertRequest
    ) -> ProgressResponse:
        algorithm_id = PydanticObjectId(payload.algorithm_id)
        algorithm = await self._algorithms.get_by_id(algorithm_id)
        if algorithm is None:
            raise NotFoundError("That problem does not exist.")

        record = await self._progress.upsert(
            user_id=user_id,
            algorithm_id=algorithm_id,
            status=payload.status,
            time_spent_ms=payload.time_spent_ms,
            hint_used=payload.hint_used,
        )

        event_type = (
            AnalyticsEventType.PROBLEM_SOLVED
            if payload.status == ProgressStatus.SOLVED
            else AnalyticsEventType.PROBLEM_ATTEMPTED
        )
        await self._analytics.record(user_id, event_type, {"algorithm_id": str(algorithm_id)})

        return ProgressResponse(
            algorithm_id=str(record.algorithm_id),
            status=record.status,
            attempts=record.attempts,
            best_time_ms=record.best_time_ms,
            hints_used=record.hints_used,
            last_attempt_at=record.last_attempt_at,
            solved_at=record.solved_at,
        )

    async def list_for_user(self, user_id: PydanticObjectId) -> list[ProgressResponse]:
        records = await self._progress.list_for_user(user_id)
        return [
            ProgressResponse(
                algorithm_id=str(record.algorithm_id),
                status=record.status,
                attempts=record.attempts,
                best_time_ms=record.best_time_ms,
                hints_used=record.hints_used,
                last_attempt_at=record.last_attempt_at,
                solved_at=record.solved_at,
            )
            for record in records
        ]
