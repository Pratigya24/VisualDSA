from fastapi import Request

from app.core.exceptions import RateLimitExceededError
from app.core.redis_client import get_redis

# Atomic token-bucket refill + consume, executed server-side in Redis so concurrent
# requests from the same key can never race past the limit.
_TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_per_second = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local bucket = redis.call('HMGET', key, 'tokens', 'updated_at')
local tokens = tonumber(bucket[1])
local updated_at = tonumber(bucket[2])

if tokens == nil then
  tokens = capacity
  updated_at = now
end

local elapsed = math.max(0, now - updated_at)
tokens = math.min(capacity, tokens + elapsed * refill_per_second)

local allowed = 0
if tokens >= requested then
  tokens = tokens - requested
  allowed = 1
end

redis.call('HMSET', key, 'tokens', tokens, 'updated_at', now)
redis.call('EXPIRE', key, 3600)

return {allowed, tokens}
"""


class RateLimiter:
    """Per-key token bucket. Instantiate once per policy (default vs AI) and use
    as a FastAPI dependency: `Depends(ai_rate_limiter)`.
    """

    def __init__(self, *, requests_per_minute: int, bucket_name: str):
        self.capacity = requests_per_minute
        self.refill_per_second = requests_per_minute / 60.0
        self.bucket_name = bucket_name

    async def __call__(self, request: Request) -> None:
        redis = get_redis()
        identity = self._identity(request)
        key = f"ratelimit:{self.bucket_name}:{identity}"

        import time

        allowed, _remaining = await redis.eval(
            _TOKEN_BUCKET_LUA,
            1,
            key,
            self.capacity,
            self.refill_per_second,
            time.time(),
            1,
        )

        if not allowed:
            raise RateLimitExceededError(
                f"Rate limit exceeded for '{self.bucket_name}'. Try again shortly."
            )

    @staticmethod
    def _identity(request: Request) -> str:
        user = getattr(request.state, "user_id", None)
        if user:
            return f"user:{user}"
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"


def get_settings_limiters():
    from app.core.config import get_settings

    settings = get_settings()
    return (
        RateLimiter(requests_per_minute=settings.rate_limit_default_per_minute, bucket_name="default"),
        RateLimiter(requests_per_minute=settings.rate_limit_ai_per_minute, bucket_name="ai"),
    )


default_rate_limiter, ai_rate_limiter = get_settings_limiters()
