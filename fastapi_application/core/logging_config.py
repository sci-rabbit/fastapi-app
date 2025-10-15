from logging.config import dictConfig


def setup_logging(log_level: str = "INFO", json: bool = False) -> None:
    formatters = {
        "plain": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "access": {
            # ✅ Исправленный форматтер
            "format": "%(asctime)s %(levelname)s uvicorn.access %(message)s",
        },
        "json": {
            "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
        },
    }
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json" if json else "plain",
                },
                "access": {
                    "class": "logging.StreamHandler",
                    "formatter": "access",
                },
            },
            "loggers": {
                "": {"handlers": ["console"], "level": log_level},
                "uvicorn": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["access"],
                    "level": log_level,
                    "propagate": False,
                },
                "sqlalchemy": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }
    )
