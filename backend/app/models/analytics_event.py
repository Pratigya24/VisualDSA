from datetime import datetime, timezone
from enum import StrEnum

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class AnalyticsEventType(StrEnum):
    PROBLEM_ATTEMPTED = "problem_attempted"
    PROBLEM_SOLVED = "problem_solved"
    NOTE_CREATED = "note_created"
    BOOKMARK_ADDED = "bookmark_added"
    LOGIN = "login"


class AnalyticsEvent(Document):
    user_id: PydanticObjectId
    event_type: AnalyticsEventType
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "analytics_events"
        indexes = [
            IndexModel([("user_id", 1), ("created_at", -1)]),
            IndexModel([("event_type", 1), ("created_at", -1)]),
            IndexModel("created_at", expireAfterSeconds=60 * 60 * 24 * 365),
        ]
