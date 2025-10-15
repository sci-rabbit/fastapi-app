from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from fastapi_application.core.config import settings
from .api_v1 import router as router_api_v1

router = APIRouter(
    prefix=settings.api.prefix,
    dependencies=[
        Depends(
            RateLimiter(
                times=settings.rate_limiter.times,
                seconds=settings.rate_limiter.seconds,
            ),
        )
    ],
)
router.include_router(router_api_v1)
