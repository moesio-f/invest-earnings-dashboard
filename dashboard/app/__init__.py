# Logging configuration
import logging
import logging.config

from . import patches

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
        "": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
        "app": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
logging.config.dictConfig(LOGGING_CONFIG)

# Streamlit logs should propagate
patches.apply_streamlit_patches()

del logging, LOGGING_CONFIG
