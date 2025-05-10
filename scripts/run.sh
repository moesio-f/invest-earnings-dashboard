#!/bin/sh

set -e

# Trick to get environment variables as system-wide.
# Required for cronjobs to inherit environment variables
# set during runtime
printenv | grep -v "no_proxy" >> /etc/environment


run_alembic="$1"
start_dashboard="$2"

# Guarantee database matches expected
cd app/
python -m alembic upgrade head
cd ../

# Start cron to run cronjobs/app routines
service cron start

# Run dashboard
python -m streamlit run app/dashboard/entrypoint.py --server.port $DASHBOARD_PORT
