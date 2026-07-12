from datetime import datetime, timezone
from enum import StrEnum

from beanie import Document, Indexed
from pydantic import EmailStr, Field
from pymongo import IndexModel


class UserRole(StrEnum):
    STUDENT = "student"
    ADMIN = "admin"


class OAuthProvider(StrEnum):
    GOOGLE = "google"


class User(Document):
    email: Indexed(EmailStr, unique=True)  # type: ignore[valid-type]
    password_hash: str | None = None
    oauth_provider: OAuthProvider | None = None
    oauth_id: str | None = None
    display_name: str
    avatar_url: str | None = None
    role: UserRole = UserRole.STUDENT
    email_verified: bool = False
    streak_count: int = 0
    last_active_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
        indexes = [
            IndexModel("email", unique=True),
            IndexModel([("oauth_provider", 1), ("oauth_id", 1)]),
        ]

    def is_password_account(self) -> bool:
        return self.password_hash is not None
