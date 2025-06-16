#!/bin/sh
# Exit on first error
set -e

# Trick to get environment variables as system-wide.
# Required for cronjobs to inherit environment variables
# set during runtime
printenv | grep -v "no_proxy" >> /etc/environment

# Guarantee database matches expected
cd app/
python -m alembic upgrade head
cd ../

# Maybe bootstrap economic
python -m app.routines.bootstrap_economic

# Start cron to run cronjobs/app routines
service cron start

# Run dashboard
python -m streamlit run app/dashboard/entrypoint.py --server.port $DASHBOARD_PORT
