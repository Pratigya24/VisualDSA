from beanie import PydanticObjectId

from app.core.exceptions import ConflictError, NotFoundError
from app.models.analytics_event import AnalyticsEventType
from app.models.progress import ProgressStatus
from app.repositories.algorithm_repository import AlgorithmRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.algorithm import AlgorithmSummaryResponse
from app.schemas.bookmark import BookmarkResponse


class BookmarkService:
    def __init__(
        self,
        bookmark_repository: BookmarkRepository,
        algorithm_repository: AlgorithmRepository,
        analytics_repository: AnalyticsRepository,
        progress_repository: ProgressRepository,
    ) -> None:
        self._bookmarks = bookmark_repository
        self._algorithms = algorithm_repository
        self._analytics = analytics_repository
        self._progress = progress_repository

    async def list_for_user(self, user_id: PydanticObjectId) -> list[BookmarkResponse]:
        bookmarks = await self._bookmarks.list_for_user(user_id)
        algorithms = await self._algorithms.get_many_by_ids([b.algorithm_id for b in bookmarks])
        algorithm_by_id = {algo.id: algo for algo in algorithms}

        responses: list[BookmarkResponse] = []
        for bookmark in bookmarks:
            algorithm = algorithm_by_id.get(bookmark.algorithm_id)
            if algorithm is None:
                continue
            progress = await self._progress.get(user_id, algorithm.id)
            responses.append(
                BookmarkResponse(
                    algorithm=AlgorithmSummaryResponse(
                        id=str(algorithm.id),
                        slug=algorithm.slug,
                        title=algorithm.title,
                        difficulty=algorithm.difficulty,
                        topic_id=str(algorithm.topic_id),
                        pattern_tags=algorithm.pattern_tags,
                        companies=algorithm.companies,
                        estimated_minutes=algorithm.estimated_minutes,
                        status=progress.status if progress else ProgressStatus.NOT_STARTED,
                        is_bookmarked=True,
                    ),
                    created_at=bookmark.created_at,
                )
            )
        return responses

    async def create(self, user_id: PydanticObjectId, algorithm_id: PydanticObjectId) -> None:
        algorithm = await self._algorithms.get_by_id(algorithm_id)
        if algorithm is None:
            raise NotFoundError("That problem does not exist.")
        if await self._bookmarks.exists(user_id, algorithm_id):
            raise ConflictError("This problem is already bookmarked.")
        await self._bookmarks.create(user_id, algorithm_id)
        await self._analytics.record(
            user_id, AnalyticsEventType.BOOKMARK_ADDED, {"algorithm_id": str(algorithm_id)}
        )

    async def delete(self, user_id: PydanticObjectId, algorithm_id: PydanticObjectId) -> None:
        deleted = await self._bookmarks.delete(user_id, algorithm_id)
        if not deleted:
            raise NotFoundError("Bookmark not found.")
