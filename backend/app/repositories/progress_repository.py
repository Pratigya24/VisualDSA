from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.models.progress import Progress, ProgressStatus


class ProgressRepository:
    async def get(self, user_id: PydanticObjectId, algorithm_id: PydanticObjectId) -> Progress | None:
        return await Progress.find_one(
            Progress.user_id == user_id,
            Progress.algorithm_id == algorithm_id,
        )

    async def list_for_user(
        self, user_id: PydanticObjectId, *, status: ProgressStatus | None = None
    ) -> list[Progress]:
        query: dict = {"user_id": user_id}
        if status is not None:
            query["status"] = status
        return await Progress.find(query).to_list()

    async def upsert(
        self,
        *,
        user_id: PydanticObjectId,
        algorithm_id: PydanticObjectId,
        status: ProgressStatus,
        time_spent_ms: int | None,
        hint_used: bool,
    ) -> Progress:
        record = await self.get(user_id, algorithm_id)
        now = datetime.now(timezone.utc)

        if record is None:
            record = Progress(user_id=user_id, algorithm_id=algorithm_id)

        record.status = status
        record.attempts += 1
        record.last_attempt_at = now
        if hint_used:
            record.hints_used += 1
        if time_spent_ms is not None and (record.best_time_ms is None or time_spent_ms < record.best_time_ms):
            record.best_time_ms = time_spent_ms
        if status == ProgressStatus.SOLVED and record.solved_at is None:
            record.solved_at = now

        await record.save()
        return record

    async def count_solved(self, user_id: PydanticObjectId) -> int:
        return await Progress.find(
            Progress.user_id == user_id, Progress.status == ProgressStatus.SOLVED
        ).count()
