"""Funções utilitárias para
carregamento de backups.
"""

import logging
from pathlib import Path

import click
import invest_earning.database
import pandas as pd
import sqlalchemy as sa

LOGGER = logging.getLogger(__name__)


@click.command()
@click.option("--db_url", help="String de conexão com o banco de dados.")
@click.option("--declarative_base", help="Identificador da base declarativa do banco.")
@click.option(
    "--data_path",
    help="Caminho para dados gerados através do comando `parquet_backup`.",
)
@click.option("--skip_table", multiple=True, default=[])
def load_parquet_backup(
    db_url: str, declarative_base: str, data_path: str, skip_table: list[str]
):
    # Find base
    Base = getattr(invest_earning.database.base, declarative_base)
    tables = Base.metadata.tables
    skip_tables = [tables[s] for s in skip_table]

    # Find data
    data_path = Path(data_path)
    directories = list(sorted(p.parent for p in data_path.rglob("metadata.json")))
    if len(directories) < 1:
        LOGGER.warning(
            "There are no backups to load in %s. Skipping this routine.", data_path
        )
        return

    # Find the most recent backup
    most_recent = directories[0]

    # Find paths and table names
    tables_and_paths = sorted(
        [
            (tables[p.name.replace(".parquet", "")], p)
            for p in most_recent.rglob("*.parquet")
        ],
        key=lambda v: Base.metadata.sorted_tables.index(v[0]),
    )

    # Remove skipped tables
    tables_and_paths = [e for e in tables_and_paths if e[0] not in skip_tables]

    # Create session
    session = sa.orm.Session(sa.create_engine(db_url))

    # Quick check whether DB is empty
    is_db_empty = not any(
        session.query(table).count() > 0 for table, _ in tables_and_paths
    )

    # Commit and close
    if is_db_empty:
        for table, path in tables_and_paths:
            # Load parquet
            df = pd.read_parquet(path)

            # Execute insert
            session.execute(sa.insert(table), df.to_dict(orient="records"))

        # Commit all changes
        session.commit()
    else:
        LOGGER.warning("Tried to load backup on non-empty database. Skipping routine.")

    session.close()


if __name__ == "__main__":
    load_parquet_backup()
