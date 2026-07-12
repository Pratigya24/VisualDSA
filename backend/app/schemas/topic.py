from pydantic import BaseModel


class TopicResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    order: int
    prerequisite_ids: list[str]
    icon: str | None
    is_unlocked: bool
    algorithm_count: int
    solved_count: int


class TopicListResponse(BaseModel):
    topics: list[TopicResponse]
