import structlog
from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    """Returns the process-wide Motor client. Raises if `connect_to_mongo` hasn't run."""
    if _client is None:
        raise RuntimeError("MongoDB client is not initialized. Call connect_to_mongo() first.")
    return _client


@retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(PyMongoError),
)
async def connect_to_mongo(document_models: list[type[Document]]) -> None:
    """Opens the Motor client and initializes Beanie against the configured database.

    `document_models` is supplied by the application composition root (main.py),
    which is the only place allowed to know about every Document subclass across
    every feature module — this keeps core/database.py decoupled from models/.
    """
    global _client
    settings = get_settings()

    logger.info("mongodb.connecting", uri_host=_redact_uri(settings.mongodb_uri))
    _client = AsyncIOMotorClient(settings.mongodb_uri, uuidRepresentation="standard")

    # Fail fast on unreachable clusters instead of deferring the error to first query.
    await _client.admin.command("ping")

    await init_beanie(
        database=_client[settings.mongodb_db_name],
        document_models=document_models,
    )
    logger.info("mongodb.connected", database=settings.mongodb_db_name, models=len(document_models))


async def close_mongo_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("mongodb.disconnected")


def _redact_uri(uri: str) -> str:
    """Strips credentials from a Mongo URI before it ever hits a log line."""
    if "@" in uri:
        scheme, _, rest = uri.partition("://")
        _, _, host_part = rest.partition("@")
        return f"{scheme}://***@{host_part}"
    return uri
