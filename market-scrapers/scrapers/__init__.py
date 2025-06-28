# Logging configuration
from logging import config

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(name)s][%(funcName)s][%(levelname)s]: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "scrapers": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
        "__main__": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
config.dictConfig(LOGGING_CONFIG)
del config, LOGGING_CONFIG
