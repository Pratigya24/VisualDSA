from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel):
    items: list
    page: int
    limit: int
    total: int
    total_pages: int

    @classmethod
    def build(cls, items: list, page: int, limit: int, total: int) -> "PaginatedResponse":
        total_pages = (total + limit - 1) // limit if limit else 0
        return cls(items=items, page=page, limit=limit, total=total, total_pages=total_pages)
