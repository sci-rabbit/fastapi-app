import structlog
import uvicorn

from fastapi_application.api import router as api_router
from fastapi_application.core.config import settings
from fastapi_application.create_fastapi_app import create_app

from fastapi_application.core.logging_config import setup_logging


setup_logging(log_level=settings.logging.level, json=False)
logger = structlog.get_logger()


main_app = create_app()

main_app.include_router(
    api_router,
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
