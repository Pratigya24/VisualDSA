from dataclasses import dataclass

from app.core.config import get_settings
from app.core.exceptions import ConflictError, UnauthorizedError, ValidationFailedError
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.token_store import TokenStore
from app.models.user import OAuthProvider, User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    refresh_jti: str
    expires_in: int


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_store: TokenStore,
        email_service: EmailService,
    ) -> None:
        self._users = user_repository
        self._tokens = token_store
        self._email = email_service
        self._settings = get_settings()

    # ---- Registration / login ----

    async def register(self, email: str, password: str, display_name: str) -> tuple[User, TokenPair]:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise ConflictError("An account with this email already exists.")

        user = User(
            email=email,
            password_hash=hash_password(password),
            display_name=display_name,
            role=UserRole.STUDENT,
        )
        user = await self._users.create(user)

        verification_token = await self._tokens.create_email_verification_token(str(user.id))
        verification_url = (
            f"{self._settings.frontend_base_url}/verify-email?token={verification_token}"
        )
        await self._email.send_verification_email(user.email, verification_url)

        tokens = await self._issue_token_pair(user)
        return user, tokens

    async def login(self, email: str, password: str) -> tuple[User, TokenPair]:
        user = await self._users.get_by_email(email)
        if user is None or not user.is_password_account():
            raise UnauthorizedError("Incorrect email or password.")
        if not verify_password(password, user.password_hash):  # type: ignore[arg-type]
            raise UnauthorizedError("Incorrect email or password.")

        await self._users.touch_last_active(user)
        tokens = await self._issue_token_pair(user)
        return user, tokens

    async def login_or_register_with_google(
        self, oauth_id: str, email: str, display_name: str, avatar_url: str | None
    ) -> tuple[User, TokenPair]:
        user = await self._users.get_by_oauth(OAuthProvider.GOOGLE, oauth_id)
        if user is None:
            user = await self._users.get_by_email(email)

        if user is None:
            user = User(
                email=email,
                display_name=display_name,
                avatar_url=avatar_url,
                oauth_provider=OAuthProvider.GOOGLE,
                oauth_id=oauth_id,
                email_verified=True,
                role=UserRole.STUDENT,
            )
            user = await self._users.create(user)
        elif user.oauth_provider is None:
            # An email/password account signing in with Google for the first time —
            # link the accounts rather than creating a duplicate.
            user.oauth_provider = OAuthProvider.GOOGLE
            user.oauth_id = oauth_id
            user.email_verified = True
            user = await self._users.update(user)

        await self._users.touch_last_active(user)
        tokens = await self._issue_token_pair(user)
        return user, tokens

    # ---- Token lifecycle ----

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token, TokenType.REFRESH)
        except Exception as exc:  # InvalidTokenError
            raise UnauthorizedError("Refresh token is invalid or expired.") from exc

        if not await self._tokens.is_refresh_jti_allowed(payload.jti, payload.sub):
            raise UnauthorizedError("Refresh token has been revoked.")

        user = await self._users.get_by_id(payload.sub)
        if user is None:
            raise UnauthorizedError("Account no longer exists.")

        # Rotate: revoke the presented refresh token and issue a brand new pair.
        # This bounds the blast radius of a leaked refresh token to a single use.
        await self._tokens.revoke_refresh_jti(payload.jti)
        return await self._issue_token_pair(user)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token, TokenType.REFRESH)
        except Exception:
            return  # already invalid/expired — nothing to revoke
        await self._tokens.revoke_refresh_jti(payload.jti)

    async def _issue_token_pair(self, user: User) -> TokenPair:
        access_token = create_access_token(str(user.id))
        refresh_token, refresh_jti = create_refresh_token(str(user.id))
        await self._tokens.allow_refresh_jti(
            refresh_jti, str(user.id), self._settings.refresh_token_expire_days * 24 * 3600
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            refresh_jti=refresh_jti,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    # ---- Email verification ----

    async def verify_email(self, token: str) -> User:
        user_id = await self._tokens.consume_email_verification_token(token)
        if user_id is None:
            raise ValidationFailedError("This verification link is invalid or has expired.")

        user = await self._users.get_by_id(user_id)
        if user is None:
            raise ValidationFailedError("This verification link is invalid or has expired.")

        user.email_verified = True
        return await self._users.update(user)

    # ---- Password reset ----

    async def request_password_reset(self, email: str) -> None:
        user = await self._users.get_by_email(email)
        if user is None or not user.is_password_account():
            # Deliberately silent: responding identically whether or not the
            # account exists prevents email enumeration via this endpoint.
            return

        reset_token = await self._tokens.create_password_reset_token(str(user.id))
        reset_url = f"{self._settings.frontend_base_url}/reset-password?token={reset_token}"
        await self._email.send_password_reset_email(user.email, reset_url)

    async def reset_password(self, token: str, new_password: str) -> None:
        user_id = await self._tokens.consume_password_reset_token(token)
        if user_id is None:
            raise ValidationFailedError("This reset link is invalid or has expired.")

        user = await self._users.get_by_id(user_id)
        if user is None:
            raise ValidationFailedError("This reset link is invalid or has expired.")

        user.password_hash = hash_password(new_password)
        await self._users.update(user)
