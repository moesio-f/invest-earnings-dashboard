#!/bin/sh
# Exit on first error
set -e

# Dump backup for both
python -m invest_earning.database.routines.load_backup --db_url "$WALLET_DB_URL" --declarative_base WalletBase --data_path $BACKUP_DUMP_PATH/wallet --skip_table economic_data
python -m invest_earning.database.routines.load_backup --db_url "$ANALYTIC_DB_URL" --declarative_base AnalyticBase --data_path $BACKUP_DUMP_PATH/analytic
