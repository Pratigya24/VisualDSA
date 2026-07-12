from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class Topic(Document):
    name: str
    slug: Indexed(str, unique=True)  # type: ignore[valid-type]
    description: str
    order: int
    prerequisite_ids: list[PydanticObjectId] = Field(default_factory=list)
    icon: str | None = None

    class Settings:
        name = "topics"
        indexes = [
            IndexModel("slug", unique=True),
            IndexModel("order"),
        ]
