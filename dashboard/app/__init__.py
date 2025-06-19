# Logging configuration
from logging import config

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {"format": "[%(module)s][%(levelname)s]: %(message)s"},
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
        "app.wallet": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
config.dictConfig(LOGGING_CONFIG)
del config, LOGGING_CONFIG
