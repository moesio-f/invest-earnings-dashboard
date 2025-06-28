"""Conexão com o banco."""

import sqlalchemy as sa
import sqlalchemy.orm

from .config import CONFIG

engine = sa.create_engine(CONFIG.db_url)


def get_db_session() -> sa.orm.Session:
    with sa.orm.Session(engine, expire_on_commit=False) as session:
        return session
