from redis import Redis
from rq import Worker

from app.core.config import settings
from app.core.queue import INGESTION_QUEUE_NAME


def main() -> None:
    redis_connection = Redis.from_url(settings.REDIS_URL)
    worker = Worker([INGESTION_QUEUE_NAME], connection=redis_connection)
    worker.work()


if __name__ == "__main__":
    main()
