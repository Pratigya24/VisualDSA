from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.api.deps import get_bookmark_service, get_current_user
from app.models.user import User
from app.schemas.bookmark import BookmarkCreateRequest, BookmarkResponse
from app.services.bookmark_service import BookmarkService

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("", response_model=list[BookmarkResponse])
async def list_bookmarks(
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_service: Annotated[BookmarkService, Depends(get_bookmark_service)],
) -> list[BookmarkResponse]:
    return await bookmark_service.list_for_user(current_user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    payload: BookmarkCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_service: Annotated[BookmarkService, Depends(get_bookmark_service)],
) -> dict[str, str]:
    await bookmark_service.create(current_user.id, PydanticObjectId(payload.algorithm_id))
    return {"status": "created"}


@router.delete("/{algorithm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    algorithm_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_service: Annotated[BookmarkService, Depends(get_bookmark_service)],
) -> None:
    await bookmark_service.delete(current_user.id, PydanticObjectId(algorithm_id))
