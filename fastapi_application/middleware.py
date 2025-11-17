import structlog
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        corr_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=corr_id)

        logger.info(
            "Request started",
            path=request.url.path,
            method=request.method,
            correlation_id=corr_id,
        )

        try:
            response = await call_next(request)

            logger.info(
                "Request finished",
                correlation_id=corr_id,
                status_code=response.status_code,
            )

            response.headers["X-Request-ID"] = corr_id
            return response

        except Exception as e:
            logger.error(
                "Request failed",
                correlation_id=corr_id,
                error=str(e),
                exc_info=True,
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()
