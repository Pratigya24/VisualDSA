from datetime import datetime

from pydantic import BaseModel

from app.schemas.algorithm import AlgorithmSummaryResponse


class BookmarkCreateRequest(BaseModel):
    algorithm_id: str


class BookmarkResponse(BaseModel):
    algorithm: AlgorithmSummaryResponse
    created_at: datetime
