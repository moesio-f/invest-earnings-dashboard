#!/bin/sh

set -e

run_alembic="$1"
start_dashboard="$2"

# Guarantee database matches expected
cd app/
python -m alembic upgrade head
cd ../

# Run dashboard
python -m streamlit run app/dashboard/entrypoint.py --server.port $DASHBOARD_PORT
