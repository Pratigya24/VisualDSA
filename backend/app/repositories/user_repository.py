from datetime import datetime, timezone

from app.models.user import OAuthProvider, User


class UserRepository:
    """
    Sole owner of MongoDB access for the `users` collection. `services/`
    depends on this class, never on `User` (Beanie) directly, so the ODM
    could be swapped without touching business logic.
    """

    async def get_by_id(self, user_id: str) -> User | None:
        return await User.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await User.find_one(User.email == email.lower())

    async def get_by_oauth(self, provider: OAuthProvider, oauth_id: str) -> User | None:
        return await User.find_one(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id,
        )

    async def create(self, user: User) -> User:
        user.email = user.email.lower()
        await user.insert()
        return user

    async def update(self, user: User) -> User:
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
        return user

    async def touch_last_active(self, user: User) -> None:
        user.last_active_at = datetime.now(timezone.utc)
        await user.save()
