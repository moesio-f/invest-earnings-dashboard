#!/bin/sh
# Exit on first error
set -e

# Apply migrations for databases
cd common/migrations
DB_URL="$WALLET_DB_URL" python -m alembic -n wallet upgrade head
DB_URL="$ANALYTIC_DB_URL" python -m alembic -n analytic upgrade head
cd ..

# Maybe bootstrap economic data into wallet
python -m invest_earning.database.routines.bootstrap_economic --db_url "$WALLET_DB_URL" --data_path $BOOTSTRAP_DATA_PATH

