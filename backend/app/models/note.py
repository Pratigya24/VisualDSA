from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class Note(Document):
    user_id: PydanticObjectId
    algorithm_id: PydanticObjectId | None = None
    title: str
    content_md: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "notes"
        indexes = [
            IndexModel([("user_id", 1), ("algorithm_id", 1)]),
            IndexModel([("user_id", 1), ("updated_at", -1)]),
        ]
