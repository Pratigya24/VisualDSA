from app.core.exceptions import UnauthorizedError, ValidationFailedError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import ChangePasswordRequest, UpdateProfileRequest


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def update_profile(self, user: User, payload: UpdateProfileRequest) -> User:
        if payload.display_name is not None:
            user.display_name = payload.display_name
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url
        return await self._users.update(user)

    async def change_password(self, user: User, payload: ChangePasswordRequest) -> None:
        if not user.is_password_account():
            raise ValidationFailedError(
                "This account signs in with Google and has no password to change."
            )
        if not verify_password(payload.current_password, user.password_hash):  # type: ignore[arg-type]
            raise UnauthorizedError("Current password is incorrect.")

        user.password_hash = hash_password(payload.new_password)
        await self._users.update(user)
