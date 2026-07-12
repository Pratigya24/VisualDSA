from beanie import PydanticObjectId

from app.models.topic import Topic


class TopicRepository:
    async def list_all(self) -> list[Topic]:
        return await Topic.find_all().sort(Topic.order).to_list()

    async def get_by_slug(self, slug: str) -> Topic | None:
        return await Topic.find_one(Topic.slug == slug)

    async def get_by_id(self, topic_id: PydanticObjectId) -> Topic | None:
        return await Topic.get(topic_id)

    async def get_many_by_ids(self, topic_ids: list[PydanticObjectId]) -> list[Topic]:
        if not topic_ids:
            return []
        return await Topic.find({"_id": {"$in": topic_ids}}).to_list()
