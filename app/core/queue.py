from redis import Redis
from rq import Queue

from app.core.config import settings

INGESTION_QUEUE_NAME = "ingestion"


def get_redis_connection() -> Redis:
    return Redis.from_url(settings.REDIS_URL)


def get_ingestion_queue() -> Queue:
    return Queue(INGESTION_QUEUE_NAME, connection=get_redis_connection())


def enqueue_ingestion_job(job_id: str) -> None:
    queue = get_ingestion_queue()
    queue.enqueue(
        "app.services.ingestion.process_ingestion_job",
        job_id,
        job_id=job_id,
        failure_ttl=7 * 24 * 60 * 60,
        result_ttl=24 * 60 * 60,
    )
