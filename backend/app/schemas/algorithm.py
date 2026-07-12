from pydantic import BaseModel

from app.models.algorithm import Difficulty
from app.models.progress import ProgressStatus


class AlgorithmSummaryResponse(BaseModel):
    id: str
    slug: str
    title: str
    difficulty: Difficulty
    topic_id: str
    pattern_tags: list[str]
    companies: list[str]
    estimated_minutes: int
    status: ProgressStatus
    is_bookmarked: bool


class AlgorithmDetailResponse(AlgorithmSummaryResponse):
    statement_md: str
    time_complexity: str
    space_complexity: str
    plugin_key: str


class AlgorithmListResponse(BaseModel):
    items: list[AlgorithmSummaryResponse]
    page: int
    limit: int
    total: int
    total_pages: int
