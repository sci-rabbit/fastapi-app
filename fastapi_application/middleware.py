import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("request")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        corr_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        logger.info(
            "Request started",
            extra={
                "corr_id": corr_id,
                "path": request.url.path,
                "method": request.method,
            },
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = corr_id
        logger.info(
            "Request finished",
            extra={"corr_id": corr_id, "status_code": response.status_code},
        )
        return response
