from sqlalchemy import event

# SQLite FK support
from sqlalchemy.engine import Engine

from . import analytic, logging, wallet


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    import sqlite3

    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


del Engine, event, _set_sqlite_pragma
