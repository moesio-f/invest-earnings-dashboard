# Logging configuration
from logging import config

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {"format": "[%(module)s][%(levelname)s]: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
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
        "app": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "__main__": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
config.dictConfig(LOGGING_CONFIG)
del config, LOGGING_CONFIG

from sqlalchemy import event

# SQLite FK support
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


del Engine, event, _set_sqlite_pragma
