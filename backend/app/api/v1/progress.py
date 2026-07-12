from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_progress_service
from app.models.user import User
from app.schemas.progress import ProgressResponse, ProgressUpsertRequest
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=list[ProgressResponse])
async def list_progress(
    current_user: Annotated[User, Depends(get_current_user)],
    progress_service: Annotated[ProgressService, Depends(get_progress_service)],
) -> list[ProgressResponse]:
    return await progress_service.list_for_user(current_user.id)


@router.post("", response_model=ProgressResponse, status_code=status.HTTP_200_OK)
async def upsert_progress(
    payload: ProgressUpsertRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    progress_service: Annotated[ProgressService, Depends(get_progress_service)],
) -> ProgressResponse:
    return await progress_service.upsert(current_user.id, payload)
