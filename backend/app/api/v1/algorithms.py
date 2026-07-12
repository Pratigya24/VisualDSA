from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_algorithm_service, get_current_user, get_pagination
from app.models.algorithm import Difficulty
from app.models.user import User
from app.schemas.algorithm import AlgorithmDetailResponse, AlgorithmListResponse
from app.schemas.common import PaginationParams
from app.services.algorithm_service import AlgorithmService

router = APIRouter(prefix="/algorithms", tags=["algorithms"])


@router.get("", response_model=AlgorithmListResponse)
async def list_algorithms(
    current_user: Annotated[User, Depends(get_current_user)],
    algorithm_service: Annotated[AlgorithmService, Depends(get_algorithm_service)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    topic_id: Annotated[str | None, Query()] = None,
    difficulty: Annotated[Difficulty | None, Query()] = None,
    company: Annotated[str | None, Query()] = None,
    pattern: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query(max_length=100)] = None,
) -> AlgorithmListResponse:
    return await algorithm_service.list_algorithms(
        current_user.id,
        page=pagination.page,
        limit=pagination.limit,
        topic_id=PydanticObjectId(topic_id) if topic_id else None,
        difficulty=difficulty,
        company=company,
        pattern=pattern,
        search=search,
    )


@router.get("/{slug}", response_model=AlgorithmDetailResponse)
async def get_algorithm(
    slug: str,
    current_user: Annotated[User, Depends(get_current_user)],
    algorithm_service: Annotated[AlgorithmService, Depends(get_algorithm_service)],
) -> AlgorithmDetailResponse:
    return await algorithm_service.get_detail(slug, current_user.id)
