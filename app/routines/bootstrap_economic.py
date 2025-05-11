"""Funções utilitárias para
geração de backups programáticas.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from app.config import DB_CONFIG
from app.db.models import EconomicData

LOGGER = logging.getLogger(__name__)


def maybe_load_economic_data(db: str = None, data_path: str = None):
    if db is None:
        db = DB_CONFIG.connection_string

    data_path = DB_CONFIG.db_bootstrap_data_path if data_path is None else data_path
    if data_path is None:
        LOGGER.warning(
            "Data path for bootstrap not set (`DB_BOOTSTRAP_DATA_PATH`) "
            "skipping routine."
        )
        return

    # Write each parquet from data path to database
    engine = sa.create_engine(db)
    economic = data_path.joinpath(f"{EconomicData.__tablename__}.parquet")
    if not economic.exists():
        LOGGER.warning(
            f"Economic data parquet ({economic}) not found. Skipping routine."
        )
        return

    # Load DataFrame and insert into DB if it is empty
    has_data = False
    with sa_orm.Session(engine) as session:
        has_data = session.query(EconomicData).count() > 0

    if not has_data:
        df = pd.read_parquet(economic)
        df.to_sql(EconomicData.__tablename__, engine, if_exists="append", index=False)
        LOGGER.info("Inserted economic data into table database.")
    else:
        LOGGER.info("Economic data not empty, skipping routine.")


if __name__ == "__main__":
    maybe_load_economic_data()
