import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError

logger = structlog.get_logger()


def register_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(ValidationError)
    def handle_pydantic_validation_error(
        request: Request,
        exc: ValidationError,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Validation error",
                "error": exc.errors(),
            },
        )

    @app.exception_handler(IntegrityError)  # ← ДОБАВИТЬ
    def handle_integrity_error(
        request: Request,
        exc: IntegrityError,
    ) -> ORJSONResponse:
        logger.warning("Integrity error occurred", exc_info=exc)
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Data integrity violation",
                "error": "The operation violates database constraints",
            },
        )

    @app.exception_handler(DatabaseError)
    def handle_db_error(
        request: Request,
        exc: DatabaseError,
    ) -> ORJSONResponse:
        logger.error(
            "Unhandled database error",
            exc_info=exc,
        )
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error has occurred. "
                "Our admins are already working on it."
            },
        )
