import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.utils.logger import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        # attach request_id to state for handlers to use if needed
        request.state.request_id = request_id

        start = time.time()
        try:
            response = await call_next(request)
        except Exception as e:
            # let exception handlers handle it — but log here too
            logger.exception("Unhandled exception", extra={"request_id": request_id})
            raise
        duration = (time.time() - start) * 1000.0
        logger.info(
            f"{request.method} {request.url.path} completed_in={duration:.2f}ms status_code={response.status_code}",
            extra={"request_id": request_id}
        )

        # add request id to response headers so clients can correlate
        response.headers["X-Request-ID"] = request_id
        return response
