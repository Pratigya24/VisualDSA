from fastapi import APIRouter

from app.api.v1.algorithms import router as algorithms_router
from app.api.v1.auth import router as auth_router
from app.api.v1.bookmarks import router as bookmarks_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router
from app.api.v1.notes import router as notes_router
from app.api.v1.progress import router as progress_router
from app.api.v1.topics import router as topics_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(dashboard_router)
api_router.include_router(topics_router)
api_router.include_router(algorithms_router)
api_router.include_router(progress_router)
api_router.include_router(bookmarks_router)
api_router.include_router(notes_router)

# Remaining feature routers (visualizer, ai, interview, contest, ...) are
# included here as each later module ships.
