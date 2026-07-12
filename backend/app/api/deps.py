from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import InvalidTokenError, TokenType, decode_token
from app.core.token_store import TokenStore
from app.models.user import User, UserRole
from app.repositories.algorithm_repository import AlgorithmRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.topic_repository import TopicRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginationParams
from app.services.algorithm_service import AlgorithmService
from app.services.auth_service import AuthService
from app.services.bookmark_service import BookmarkService
from app.services.dashboard_service import DashboardService
from app.services.email_service import ConsoleEmailService, EmailService
from app.services.note_service import NoteService
from app.services.progress_service import ProgressService
from app.services.topic_service import TopicService
from app.services.user_service import UserService


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit)


# ---- Service/repository wiring ----
# Simple constructor-based DI: each getter builds its dependencies fresh
# per request. These are cheap (no I/O at construction time) and this keeps
# FastAPI's dependency graph explicit and easy to override in tests via
# `app.dependency_overrides`, without needing a separate DI container.


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_token_store() -> TokenStore:
    return TokenStore()


def get_email_service() -> EmailService:
    return ConsoleEmailService()


def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    token_store: Annotated[TokenStore, Depends(get_token_store)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> AuthService:
    return AuthService(user_repository, token_store, email_service)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repository)


def get_topic_repository() -> TopicRepository:
    return TopicRepository()


def get_algorithm_repository() -> AlgorithmRepository:
    return AlgorithmRepository()


def get_progress_repository() -> ProgressRepository:
    return ProgressRepository()


def get_bookmark_repository() -> BookmarkRepository:
    return BookmarkRepository()


def get_note_repository() -> NoteRepository:
    return NoteRepository()


def get_analytics_repository() -> AnalyticsRepository:
    return AnalyticsRepository()


def get_topic_service(
    topic_repository: Annotated[TopicRepository, Depends(get_topic_repository)],
    algorithm_repository: Annotated[AlgorithmRepository, Depends(get_algorithm_repository)],
    progress_repository: Annotated[ProgressRepository, Depends(get_progress_repository)],
) -> TopicService:
    return TopicService(topic_repository, algorithm_repository, progress_repository)


def get_algorithm_service(
    algorithm_repository: Annotated[AlgorithmRepository, Depends(get_algorithm_repository)],
    progress_repository: Annotated[ProgressRepository, Depends(get_progress_repository)],
    bookmark_repository: Annotated[BookmarkRepository, Depends(get_bookmark_repository)],
) -> AlgorithmService:
    return AlgorithmService(algorithm_repository, progress_repository, bookmark_repository)


def get_progress_service(
    progress_repository: Annotated[ProgressRepository, Depends(get_progress_repository)],
    algorithm_repository: Annotated[AlgorithmRepository, Depends(get_algorithm_repository)],
    analytics_repository: Annotated[AnalyticsRepository, Depends(get_analytics_repository)],
) -> ProgressService:
    return ProgressService(progress_repository, algorithm_repository, analytics_repository)


def get_bookmark_service(
    bookmark_repository: Annotated[BookmarkRepository, Depends(get_bookmark_repository)],
    algorithm_repository: Annotated[AlgorithmRepository, Depends(get_algorithm_repository)],
    analytics_repository: Annotated[AnalyticsRepository, Depends(get_analytics_repository)],
    progress_repository: Annotated[ProgressRepository, Depends(get_progress_repository)],
) -> BookmarkService:
    return BookmarkService(bookmark_repository, algorithm_repository, analytics_repository, progress_repository)


def get_note_service(
    note_repository: Annotated[NoteRepository, Depends(get_note_repository)],
    analytics_repository: Annotated[AnalyticsRepository, Depends(get_analytics_repository)],
) -> NoteService:
    return NoteService(note_repository, analytics_repository)


def get_dashboard_service(
    progress_repository: Annotated[ProgressRepository, Depends(get_progress_repository)],
    algorithm_repository: Annotated[AlgorithmRepository, Depends(get_algorithm_repository)],
    analytics_repository: Annotated[AnalyticsRepository, Depends(get_analytics_repository)],
    bookmark_repository: Annotated[BookmarkRepository, Depends(get_bookmark_repository)],
) -> DashboardService:
    return DashboardService(progress_repository, algorithm_repository, analytics_repository, bookmark_repository)


# ---- Authentication ----

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    if credentials is None:
        raise UnauthorizedError("Authentication required.")

    try:
        payload = decode_token(credentials.credentials, TokenType.ACCESS)
    except InvalidTokenError as exc:
        raise UnauthorizedError("Access token is invalid or expired.") from exc

    user = await user_repository.get_by_id(payload.sub)
    if user is None:
        raise UnauthorizedError("Account no longer exists.")

    return user


def require_role(*allowed_roles: UserRole):
    async def _check(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError("You do not have permission to perform this action.")
        return current_user

    return _check
