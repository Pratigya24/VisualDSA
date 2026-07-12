from beanie import PydanticObjectId

from app.core.exceptions import NotFoundError
from app.models.progress import ProgressStatus
from app.models.topic import Topic
from app.repositories.algorithm_repository import AlgorithmRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.topic import TopicResponse

# A prerequisite topic is considered "cleared" once the user has solved at
# least this fraction of its problems — full mastery isn't required to move
# on, matching how the roadmap is meant to feel (progressive, not gated on
# perfection).
UNLOCK_THRESHOLD = 0.5


class TopicService:
    def __init__(
        self,
        topic_repository: TopicRepository,
        algorithm_repository: AlgorithmRepository,
        progress_repository: ProgressRepository,
    ) -> None:
        self._topics = topic_repository
        self._algorithms = algorithm_repository
        self._progress = progress_repository

    async def list_roadmap(self, user_id: PydanticObjectId) -> list[TopicResponse]:
        topics = await self._topics.list_all()
        solved_algorithm_ids = {
            record.algorithm_id
            for record in await self._progress.list_for_user(user_id, status=ProgressStatus.SOLVED)
        }

        topic_stats: dict[PydanticObjectId, tuple[int, int]] = {}
        for topic in topics:
            total = await self._algorithms.count_by_topic(topic.id)
            algorithms = await self._algorithms.list_paginated(skip=0, limit=total or 1, topic_id=topic.id)
            solved = sum(1 for algo in algorithms[0] if algo.id in solved_algorithm_ids)
            topic_stats[topic.id] = (total, solved)

        responses: list[TopicResponse] = []
        for topic in topics:
            total, solved = topic_stats.get(topic.id, (0, 0))
            is_unlocked = self._is_unlocked(topic, topic_stats)
            responses.append(
                TopicResponse(
                    id=str(topic.id),
                    name=topic.name,
                    slug=topic.slug,
                    description=topic.description,
                    order=topic.order,
                    prerequisite_ids=[str(pid) for pid in topic.prerequisite_ids],
                    icon=topic.icon,
                    is_unlocked=is_unlocked,
                    algorithm_count=total,
                    solved_count=solved,
                )
            )
        return responses

    def _is_unlocked(
        self, topic: Topic, topic_stats: dict[PydanticObjectId, tuple[int, int]]
    ) -> bool:
        if not topic.prerequisite_ids:
            return True
        for prereq_id in topic.prerequisite_ids:
            total, solved = topic_stats.get(prereq_id, (0, 0))
            if total == 0:
                continue
            if (solved / total) < UNLOCK_THRESHOLD:
                return False
        return True

    async def get_topic_detail(self, slug: str, user_id: PydanticObjectId) -> TopicResponse:
        topic = await self.get_by_slug(slug)
        all_topics = await self._topics.list_all()
        solved_algorithm_ids = {
            record.algorithm_id
            for record in await self._progress.list_for_user(user_id, status=ProgressStatus.SOLVED)
        }

        topic_stats: dict[PydanticObjectId, tuple[int, int]] = {}
        for candidate in all_topics:
            total = await self._algorithms.count_by_topic(candidate.id)
            algorithms = await self._algorithms.list_paginated(skip=0, limit=total or 1, topic_id=candidate.id)
            solved = sum(1 for algo in algorithms[0] if algo.id in solved_algorithm_ids)
            topic_stats[candidate.id] = (total, solved)

        total, solved = topic_stats.get(topic.id, (0, 0))
        return TopicResponse(
            id=str(topic.id),
            name=topic.name,
            slug=topic.slug,
            description=topic.description,
            order=topic.order,
            prerequisite_ids=[str(pid) for pid in topic.prerequisite_ids],
            icon=topic.icon,
            is_unlocked=self._is_unlocked(topic, topic_stats),
            algorithm_count=total,
            solved_count=solved,
        )

    async def get_by_slug(self, slug: str) -> Topic:
        topic = await self._topics.get_by_slug(slug)
        if topic is None:
            raise NotFoundError(f"Topic '{slug}' was not found.")
        return topic
