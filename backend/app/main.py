from contextlib import asynccontextmanager

from beanie import Document
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.database import close_mongo_connection, connect_to_mongo
from app.core.logging import configure_logging
from app.core.redis_client import close_redis_pool
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_id import RequestIDMiddleware
from app.models.algorithm import Algorithm
from app.models.analytics_event import AnalyticsEvent
from app.models.bookmark import Bookmark
from app.models.note import Note
from app.models.progress import Progress
from app.models.topic import Topic
from app.models.user import User

# Every Beanie Document across every feature module is registered here — this
# is the one place in the codebase allowed to know the full model set, so that
# core/database.py stays decoupled from individual feature modules. Populated
# as each module ships its models/ files.
DOCUMENT_MODELS: list[type[Document]] = [
    User,
    Topic,
    Algorithm,
    Progress,
    Bookmark,
    Note,
    AnalyticsEvent,
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await connect_to_mongo(DOCUMENT_MODELS)
    yield
    await close_mongo_connection()
    await close_redis_pool()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
