from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "visualdsa",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[],  # populated as task modules ship (e.g. "app.engines.ai.tasks", "app.engines.dryrun.tasks")
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=120,
    task_soft_time_limit=90,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=200,
    result_expires=3600,
    task_default_queue="default",
    task_routes={
        "app.engines.ai.tasks.*": {"queue": "ai"},
        "app.engines.dryrun.tasks.*": {"queue": "dryrun"},
    },
)
