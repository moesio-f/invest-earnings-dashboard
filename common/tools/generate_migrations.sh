#!/bin/sh

set -e

# Get script directory
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# Cd to migrations directory
cd $SCRIPT_DIR
cd ..
cd migrations

# Set temporary variables
export DB_URL="sqlite:///tmp.db"
export PYTHONPATH=../

# Upgrade temporary db to current head
python -m alembic -n $1 upgrade head

# Create new revision
python -m alembic -n $1 revision --autogenerate -m "$2"

# Delete temporary database
rm tmp.db
