from enum import StrEnum

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Algorithm(Document):
    """
    Content/catalog record for a single problem.

    `plugin_key` will resolve against the Algorithm Engine's plugin registry
    once Module 3 ships (see architecture §16); until then it's stored as
    plain metadata so Module 2's roadmap, progress, and bookmark features
    have real problems to reference. Nothing here executes anything —
    execution is exclusively Module 3's responsibility.
    """

    slug: Indexed(str, unique=True)  # type: ignore[valid-type]
    title: str
    statement_md: str
    difficulty: Difficulty
    topic_id: PydanticObjectId
    plugin_key: str
    pattern_tags: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    time_complexity: str
    space_complexity: str
    estimated_minutes: int = 20
    order: int = 0

    class Settings:
        name = "algorithms"
        indexes = [
            IndexModel("slug", unique=True),
            IndexModel("topic_id"),
            IndexModel("difficulty"),
            IndexModel("pattern_tags"),
            IndexModel("companies"),
        ]
