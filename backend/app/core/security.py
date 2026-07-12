from datetime import datetime, timedelta, timezone
from enum import StrEnum
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import get_settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    sub: str  # user id
    type: TokenType
    jti: str  # unique token id, used for refresh-token revocation in Redis
    exp: datetime
    iat: datetime


class InvalidTokenError(Exception):
    """Raised when a JWT fails signature verification, is expired, or is malformed."""


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return _pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: str) -> str:
    return _create_token(user_id, TokenType.ACCESS, get_settings().access_token_expire_minutes * 60)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """Returns (token, jti). The caller persists `jti` in Redis to allow revocation."""
    settings = get_settings()
    jti = str(uuid4())
    token = _create_token(
        user_id,
        TokenType.REFRESH,
        settings.refresh_token_expire_days * 24 * 3600,
        jti=jti,
    )
    return token, jti


def _create_token(user_id: str, token_type: TokenType, expires_in_seconds: int, jti: str | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = TokenPayload(
        sub=user_id,
        type=token_type,
        jti=jti or str(uuid4()),
        iat=now,
        exp=now + timedelta(seconds=expires_in_seconds),
    )
    return jwt.encode(
        _to_jwt_claims(payload),
        settings.jwt_private_key(),
        algorithm=settings.jwt_algorithm,
    )


def _to_jwt_claims(payload: TokenPayload) -> dict:
    """Converts the payload to raw JWT claims, encoding `exp`/`iat` as numeric
    (epoch-seconds) timestamps per RFC 7519 — `model_dump(mode="json")` would
    otherwise serialize them as ISO-8601 strings, which python-jose's claim
    validators reject.
    """
    return {
        "sub": payload.sub,
        "type": payload.type.value,
        "jti": payload.jti,
        "iat": int(payload.iat.timestamp()),
        "exp": int(payload.exp.timestamp()),
    }


def decode_token(token: str, expected_type: TokenType) -> TokenPayload:
    settings = get_settings()
    try:
        raw = jwt.decode(token, settings.jwt_public_key(), algorithms=[settings.jwt_algorithm])
        payload = TokenPayload.model_validate(raw)
    except (JWTError, ValueError) as exc:
        raise InvalidTokenError("Token signature invalid or malformed") from exc

    if payload.type != expected_type:
        raise InvalidTokenError(f"Expected {expected_type} token, got {payload.type}")

    return payload
