import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError
from app.middleware.request_id import get_request_id

logger = structlog.get_logger(__name__)


def _problem_response(
    *, status_code: int, error_type: str, title: str, detail: str, instance: str
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "type": error_type,
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": instance,
            "request_id": get_request_id(),
        },
        media_type="application/problem+json",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers every exception handler on the app. Called once from main.py.

    Kept as an explicit registration function (rather than decorators scattered
    across the codebase) so the full set of handled error types is visible in
    one place.
    """

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("app_error", error_type=exc.error_type, detail=exc.detail, path=request.url.path)
        else:
            logger.info("app_error", error_type=exc.error_type, detail=exc.detail, path=request.url.path)
        return _problem_response(
            status_code=exc.status_code,
            error_type=exc.error_type,
            title=exc.error_type.replace("_", " ").title(),
            detail=exc.detail,
            instance=str(request.url.path),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _problem_response(
            status_code=exc.status_code,
            error_type="http_error",
            title="HTTP Error",
            detail=str(exc.detail),
            instance=str(request.url.path),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="validation_failed",
            title="Validation Failed",
            detail="; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()),
            instance=str(request.url.path),
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", path=request.url.path)
        return _problem_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="internal_error",
            title="Internal Server Error",
            detail="An unexpected error occurred. It has been logged for investigation.",
            instance=str(request.url.path),
        )
