from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_user_service
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import ChangePasswordRequest, UpdateProfileRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        email_verified=user.email_verified,
        streak_count=user.streak_count,
        created_at=user.created_at,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return _to_user_response(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UpdateProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    updated = await user_service.update_profile(current_user, payload)
    return _to_user_response(updated)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    await user_service.change_password(current_user, payload)
