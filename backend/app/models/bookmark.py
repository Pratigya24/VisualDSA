from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class Bookmark(Document):
    user_id: PydanticObjectId
    algorithm_id: PydanticObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "bookmarks"
        indexes = [
            IndexModel([("user_id", 1), ("algorithm_id", 1)], unique=True),
            IndexModel([("user_id", 1), ("created_at", -1)]),
        ]
