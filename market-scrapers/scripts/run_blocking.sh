#!/bin/sh

# Exit on first error
set -e

# Infinite loop
while true
do
    echo "[run_blocking] Starting execution at $(date +%T)."

    # Run price scraper
    python -m scrapers.market_price

    # Sleep for specified time
    sleep ${SLEEP_INTERVAL:-0.5d}
done
