from beanie import PydanticObjectId

from app.models.bookmark import Bookmark


class BookmarkRepository:
    async def list_for_user(self, user_id: PydanticObjectId) -> list[Bookmark]:
        return await Bookmark.find(Bookmark.user_id == user_id).sort(-Bookmark.created_at).to_list()

    async def exists(self, user_id: PydanticObjectId, algorithm_id: PydanticObjectId) -> bool:
        record = await Bookmark.find_one(
            Bookmark.user_id == user_id, Bookmark.algorithm_id == algorithm_id
        )
        return record is not None

    async def create(self, user_id: PydanticObjectId, algorithm_id: PydanticObjectId) -> Bookmark:
        bookmark = Bookmark(user_id=user_id, algorithm_id=algorithm_id)
        await bookmark.insert()
        return bookmark

    async def delete(self, user_id: PydanticObjectId, algorithm_id: PydanticObjectId) -> bool:
        record = await Bookmark.find_one(
            Bookmark.user_id == user_id, Bookmark.algorithm_id == algorithm_id
        )
        if record is None:
            return False
        await record.delete()
        return True
