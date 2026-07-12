from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content_md: str = Field(default="", max_length=50_000)
    algorithm_id: str | None = None


class NoteUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content_md: str = Field(default="", max_length=50_000)


class NoteResponse(BaseModel):
    id: str
    title: str
    content_md: str
    algorithm_id: str | None
    created_at: datetime
    updated_at: datetime
