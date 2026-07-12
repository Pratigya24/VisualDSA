from beanie import PydanticObjectId

from app.core.exceptions import NotFoundError
from app.models.algorithm import Algorithm, Difficulty
from app.models.progress import ProgressStatus
from app.repositories.algorithm_repository import AlgorithmRepository
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.algorithm import (
    AlgorithmDetailResponse,
    AlgorithmListResponse,
    AlgorithmSummaryResponse,
)


class AlgorithmService:
    def __init__(
        self,
        algorithm_repository: AlgorithmRepository,
        progress_repository: ProgressRepository,
        bookmark_repository: BookmarkRepository,
    ) -> None:
        self._algorithms = algorithm_repository
        self._progress = progress_repository
        self._bookmarks = bookmark_repository

    async def _to_summary(
        self, algorithm: Algorithm, user_id: PydanticObjectId
    ) -> AlgorithmSummaryResponse:
        progress = await self._progress.get(user_id, algorithm.id)
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
            status=progress.status if progress else ProgressStatus.NOT_STARTED,
            is_bookmarked=is_bookmarked,
        )

    async def list_algorithms(
        self,
        user_id: PydanticObjectId,
        *,
        page: int,
        limit: int,
        topic_id: PydanticObjectId | None,
        difficulty: Difficulty | None,
        company: str | None,
        pattern: str | None,
        search: str | None,
    ) -> AlgorithmListResponse:
        skip = (page - 1) * limit
        items, total = await self._algorithms.list_paginated(
            skip=skip,
            limit=limit,
            topic_id=topic_id,
            difficulty=difficulty,
            company=company,
            pattern=pattern,
            search=search,
        )
        summaries = [await self._to_summary(item, user_id) for item in items]
        total_pages = (total + limit - 1) // limit if limit else 0
        return AlgorithmListResponse(items=summaries, page=page, limit=limit, total=total, total_pages=total_pages)

    async def get_detail(self, slug: str, user_id: PydanticObjectId) -> AlgorithmDetailResponse:
        algorithm = await self._algorithms.get_by_slug(slug)
        if algorithm is None:
            raise NotFoundError(f"Problem '{slug}' was not found.")
        summary = await self._to_summary(algorithm, user_id)
        return AlgorithmDetailResponse(
            **summary.model_dump(),
            statement_md=algorithm.statement_md,
            time_complexity=algorithm.time_complexity,
            space_complexity=algorithm.space_complexity,
            plugin_key=algorithm.plugin_key,
        )
