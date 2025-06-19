"""Funções utilitárias para
geração de backups programáticas.
"""

import logging
from pathlib import Path

import click
import pandas as pd
import sqlalchemy as sa
from invest_earning.database.wallet import EconomicData, EconomicIndex

LOGGER = logging.getLogger(__name__)


@click.command()
@click.option("--db_url", help="String de conexão com o banco de dados.")
@click.option("--data_path", help="Caminho para os dados ecônomicos.")
def maybe_load_economic_data(db_url: str, data_path: str):
    data_path = Path(data_path)

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
    with sa.orm.Session(engine) as session:
        has_data = session.query(EconomicData).count() > 0

    if not has_data:
        # Load DataFrame
        df = pd.read_parquet(economic)

        # Convert dtypes
        df["index"] = df["index"].map(EconomicIndex.from_value)
        df["reference_date"] = pd.to_datetime(df["reference_date"]).dt.date

        # Create session and add all
        with sa.orm.Session(engine) as session:
            session.execute(sa.insert(EconomicData), df.to_dict(orient="records"))
        LOGGER.info("Inserted economic data into table database.")
    else:
        LOGGER.info("Economic data not empty, skipping routine.")


if __name__ == "__main__":
    maybe_load_economic_data()
