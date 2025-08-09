from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.logger import logger

class AppException(Exception):
    """Custom domain exception for controlled errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP error: {exc.detail}", extra={"request_id": getattr(request.state, "request_id", "-")})
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation failed", extra={"request_id": getattr(request.state, "request_id", "-")})
    # compact validation errors
    errors = [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
    return JSONResponse(status_code=422, content={"error": "validation_error", "details": errors})

async def generic_exception_handler(request: Request, exc: Exception):
    # hide internal details from client, but log the stack trace
    request_id = getattr(request.state, "request_id", "-")
    logger.exception("Internal server error", extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "request_id": request_id, "message": "An unexpected error occurred."}
    )
