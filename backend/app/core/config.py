from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings, loaded from environment variables / .env.

    This is the single source of truth for configuration. No module outside
    core/ should read `os.environ` directly — everything goes through
    `get_settings()` so behavior stays testable and overridable.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "VisualDSA AI"
    environment: str = Field(default="local", pattern="^(local|staging|production)$")
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # --- MongoDB ---
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "visualdsa"

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # --- Session (Authlib OAuth state signing — NOT used for user sessions,
    # auth is JWT-based; this only secures the short-lived OAuth handshake) ---
    session_secret_key: str = "dev-only-change-me"

    # --- JWT ---
    jwt_private_key_path: str = "./keys/private.pem"
    jwt_public_key_path: str = "./keys/public.pem"
    jwt_algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # --- Google OAuth ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # --- Frontend (used to build links embedded in emails, OAuth redirects) ---
    frontend_base_url: str = "http://localhost:5173"
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # --- AI Providers ---
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # --- Rate limiting ---
    rate_limit_default_per_minute: int = 100
    rate_limit_ai_per_minute: int = 20

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        # Allows CORS_ORIGINS to be provided as a JSON list or a comma-separated string.
        if isinstance(value, str) and not value.strip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def jwt_private_key(self) -> str:
        return Path(self.jwt_private_key_path).read_text(encoding="utf-8")

    def jwt_public_key(self) -> str:
        return Path(self.jwt_public_key_path).read_text(encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. FastAPI dependencies should use this, not `Settings()`."""
    return Settings()
