import secrets

from app.core.redis_client import get_redis

_REFRESH_PREFIX = "auth:refresh_jti:"
_EMAIL_VERIFY_PREFIX = "auth:verify_email:"
_PASSWORD_RESET_PREFIX = "auth:reset_password:"


class TokenStore:
    """
    Redis-backed storage for token state that must never live in MongoDB:
    it's ephemeral (TTL-bound) and its only purpose is fast existence/
    revocation checks. This is why refresh-token jtis, email-verification
    tokens, and password-reset tokens live here rather than as `User`
    fields or a Mongo collection — Redis is explicitly cache/session/broker
    only per the architecture, and this store is exactly that.
    """

    # --- Refresh token allowlist (revocation) ---

    async def allow_refresh_jti(self, jti: str, user_id: str, ttl_seconds: int) -> None:
        await get_redis().set(f"{_REFRESH_PREFIX}{jti}", user_id, ex=ttl_seconds)

    async def is_refresh_jti_allowed(self, jti: str, user_id: str) -> bool:
        stored = await get_redis().get(f"{_REFRESH_PREFIX}{jti}")
        return stored == user_id

    async def revoke_refresh_jti(self, jti: str) -> None:
        await get_redis().delete(f"{_REFRESH_PREFIX}{jti}")

    # --- Email verification ---

    async def create_email_verification_token(self, user_id: str, ttl_seconds: int = 86400) -> str:
        token = secrets.token_urlsafe(32)
        await get_redis().set(f"{_EMAIL_VERIFY_PREFIX}{token}", user_id, ex=ttl_seconds)
        return token

    async def consume_email_verification_token(self, token: str) -> str | None:
        key = f"{_EMAIL_VERIFY_PREFIX}{token}"
        user_id = await get_redis().get(key)
        if user_id is not None:
            await get_redis().delete(key)
        return user_id

    # --- Password reset ---

    async def create_password_reset_token(self, user_id: str, ttl_seconds: int = 3600) -> str:
        token = secrets.token_urlsafe(32)
        await get_redis().set(f"{_PASSWORD_RESET_PREFIX}{token}", user_id, ex=ttl_seconds)
        return token

    async def consume_password_reset_token(self, token: str) -> str | None:
        key = f"{_PASSWORD_RESET_PREFIX}{token}"
        user_id = await get_redis().get(key)
        if user_id is not None:
            await get_redis().delete(key)
        return user_id
