import logging
import sys
from logging import Logger
from app.core.config import settings

def setup_logger(name: str = "rag_app") -> Logger:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Avoid duplicate handlers
    if not logger.hasHandlers():
        logger.addHandler(handler)

    # Add default extra so logger.info("...") doesn't fail without extra
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return record

    logging.setLogRecordFactory(record_factory)
    return logger

logger = setup_logger()
