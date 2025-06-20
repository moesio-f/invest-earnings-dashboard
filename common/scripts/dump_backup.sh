#!/bin/sh
# Exit on first error
set -e

# Dump backup for both
python -m invest_earning.database.routines.db_backup --db_url "$WALLET_DB_URL" --declarative_base WalletBase --output_path $BACKUP_DUMP_PATH/wallet
python -m invest_earning.database.routines.db_backup --db_url "$ANALYTIC_DB_URL" --declarative_base AnalyticBase --output_path $BACKUP_DUMP_PATH/analytic
