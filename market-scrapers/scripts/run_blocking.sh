#!/bin/sh

# Exit on first error
set -e

# Infinite loop
while true
do
    echo "[run_blocking] Starting execution at $(date +%T)."

    # Run price scraper
    echo "[run_blocking] Running Market Price scraper."
    python -m scrapers.market_price -f

    # Run earning scraper
    echo "[run_blocking] Running Published Earnings scraper."
    python -m scrapers.published_earnings

    # Sleep for specified time
    sleep ${SLEEP_INTERVAL:-0.5d}
done
