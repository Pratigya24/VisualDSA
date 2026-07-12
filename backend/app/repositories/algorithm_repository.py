from beanie import PydanticObjectId
from beanie.operators import In

from app.models.algorithm import Algorithm, Difficulty


class AlgorithmRepository:
    async def get_by_slug(self, slug: str) -> Algorithm | None:
        return await Algorithm.find_one(Algorithm.slug == slug)

    async def get_by_id(self, algorithm_id: PydanticObjectId) -> Algorithm | None:
        return await Algorithm.get(algorithm_id)

    async def get_many_by_ids(self, algorithm_ids: list[PydanticObjectId]) -> list[Algorithm]:
        if not algorithm_ids:
            return []
        return await Algorithm.find(In(Algorithm.id, algorithm_ids)).to_list()

    async def list_paginated(
        self,
        *,
        skip: int,
        limit: int,
        topic_id: PydanticObjectId | None = None,
        difficulty: Difficulty | None = None,
        company: str | None = None,
        pattern: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Algorithm], int]:
        query: dict = {}
        if topic_id is not None:
            query["topic_id"] = topic_id
        if difficulty is not None:
            query["difficulty"] = difficulty
        if company is not None:
            query["companies"] = company
        if pattern is not None:
            query["pattern_tags"] = pattern
        if search:
            query["title"] = {"$regex": search, "$options": "i"}

        find_query = Algorithm.find(query)
        total = await find_query.count()
        items = await find_query.sort(Algorithm.order).skip(skip).limit(limit).to_list()
        return items, total

    async def count_by_topic(self, topic_id: PydanticObjectId) -> int:
        return await Algorithm.find(Algorithm.topic_id == topic_id).count()
