"""Funções utilitárias para
geração de backups programáticas.
"""

import logging

import click
import pandas as pd
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from invest_earning.database.wallet import EconomicData

LOGGER = logging.getLogger(__name__)


@click.command()
@click.option("--db_url", help="String de conexão com o banco de dados.")
@click.argument("--data_path", help="Caminho para os dados ecônomicos.")
def maybe_load_economic_data(db_url: str, data_path: str):
    # Write each parquet from data path to database
    engine = sa.create_engine(db_url)
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
