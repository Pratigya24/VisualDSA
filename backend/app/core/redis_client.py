import structlog
from redis.asyncio import ConnectionPool, Redis

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

_pool: ConnectionPool | None = None


def get_redis() -> Redis:
    """Returns a Redis client backed by a shared connection pool.

    A new lightweight `Redis` instance is created per call (cheap — it just
    wraps the pool), so this is safe to use as a FastAPI dependency without
    leaking connections across requests.
    """
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = ConnectionPool.from_url(settings.redis_url, decode_responses=True, max_connections=50)
        logger.info("redis.pool_created")
    return Redis(connection_pool=_pool)


async def close_redis_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
        logger.info("redis.pool_closed")


async def ping_redis() -> bool:
    try:
        return await get_redis().ping()
    except Exception:  # noqa: BLE001 — health check must never raise
        return False
