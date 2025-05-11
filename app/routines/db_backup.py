"""Funções utilitárias para
geração de backups programáticas.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import sqlalchemy as sa

from app.config import DB_CONFIG
from app.db.models import Base

LOGGER = logging.getLogger(__name__)


def parquet_backup(db: str = None, output_path: str = None):
    if db is None:
        db = DB_CONFIG.connection_string

    output_path = DB_CONFIG.db_backup_path if output_path is None else output_path
    if output_path is None:
        LOGGER.warning(
            "Output path for backups not set (`DB_BACKUP_PATH`) skipping routine."
        )
        return

    # Get timestamp
    now = datetime.now()
    out_dir = Path(output_path).joinpath(now.date().isoformat())
    backup_meta = dict(timestamp=now.isoformat())
    out_dir.mkdir(exist_ok=True)

    # Write each table as a parquet
    engine = sa.create_engine(db)
    for table_name, table in Base.metadata.tables.items():
        # Query table
        stmt = str(sa.select(table).compile(engine))
        df = pd.read_sql(stmt, engine)

        # Maybe add more table metadata
        backup_meta[table_name] = dict(
            count=len(df), dtypes=df.dtypes.astype(str).to_dict()
        )
        df.to_parquet(out_dir.joinpath(f"{table_name}.parquet"))

    # Write metadata
    with out_dir.joinpath("metadata.json").open("w+") as f:
        json.dump(backup_meta, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parquet_backup()
