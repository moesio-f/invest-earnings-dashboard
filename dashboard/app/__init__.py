# Logging configuration
import logging

import streamlit

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(module)s][%(funcName)s][%(levelname)s]: %(message)s"
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
            "propagate": True,
        },
    },
}
logging.config.dictConfig(LOGGING_CONFIG)

# Streamlit logs should propagate
logging.getLogger("streamlit").propagate = True

del logging, LOGGING_CONFIG, streamlit
