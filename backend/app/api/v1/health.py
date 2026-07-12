from fastapi import APIRouter
from pydantic import BaseModel

from app.core.database import get_client
from app.core.redis_client import ping_redis

router = APIRouter(prefix="/health", tags=["health"])


class DependencyStatus(BaseModel):
    mongodb: bool
    redis: bool


class HealthResponse(BaseModel):
    status: str
    dependencies: DependencyStatus


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness/readiness probe used by the Docker HEALTHCHECK and deployment platform.

    Checks the actual dependencies (Mongo, Redis) rather than just returning 200
    unconditionally — a container that's up but can't reach its database should
    be reported unhealthy so orchestration can react.
    """
    mongo_ok = await _check_mongo()
    redis_ok = await ping_redis()

    return HealthResponse(
        status="ok" if (mongo_ok and redis_ok) else "degraded",
        dependencies=DependencyStatus(mongodb=mongo_ok, redis=redis_ok),
    )


async def _check_mongo() -> bool:
    try:
        await get_client().admin.command("ping")
        return True
    except Exception:  # noqa: BLE001 — health check must never raise
        return False
