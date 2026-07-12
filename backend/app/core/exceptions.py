class AppError(Exception):
    """Base class for all application-raised (as opposed to framework-raised) errors.

    Services and engines raise these instead of `HTTPException` — the API layer
    is the only place that knows how to translate a domain error into an HTTP
    status code (see middleware/error_handler.py), keeping `services/` and
    `engines/` free of any HTTP-specific concerns.
    """

    status_code: int = 500
    error_type: str = "internal_error"

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    status_code = 404
    error_type = "not_found"


class ConflictError(AppError):
    status_code = 409
    error_type = "conflict"


class ValidationFailedError(AppError):
    status_code = 422
    error_type = "validation_failed"


class UnauthorizedError(AppError):
    status_code = 401
    error_type = "unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    error_type = "forbidden"


class RateLimitExceededError(AppError):
    status_code = 429
    error_type = "rate_limit_exceeded"


class UpstreamServiceError(AppError):
    """Raised when a dependency (AI provider, sandbox runner) fails or times out."""

    status_code = 502
    error_type = "upstream_service_error"
